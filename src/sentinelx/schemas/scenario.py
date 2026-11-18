"""Investigation scenario contract (ground truth for evaluation).

A Scenario wraps an input alert together with the ground truth an investigation
should recover: the reference conclusion, the techniques, the decisive evidence,
what must stay unknown, and the actions that are / are not allowed. It is what
lets us evaluate an *investigation* (EVALUATION.md, family I), not merely a
triage label.

Design choices:
- The alert is embedded as a `RawAlert` (composition), NOT re-declared, so there
  is a single source of truth for the alert/event shape (schemas/alert.py).
- Strict validation (`extra="forbid"`) matches the other output-side schemas, so
  a malformed scenario fails fast instead of silently carrying junk.
- A cross-field validator guarantees that `key_evidence_event_ids` only names
  events that actually exist (in the initial alert OR the retrievable set) — the
  same "no dangling reference" principle the citation verifier enforces.

`expected_techniques` — canonical definition (EVALUATION.md, applied consistently):
- SYNTHETIC scenarios: the techniques the scenario was DESIGNED to represent
  (ground truth by construction).
- REAL (dataset-grounded) scenarios: ONLY techniques ESTABLISHED by the telemetry
  itself — the technique's defining behavior is directly logged, is not reasonably
  explained by benign activity, does NOT depend on attribution to an adversary, and
  does NOT rely on the dataset `time_label`. Anything merely "consistent with",
  inferred from a pattern, or attribution-dependent is a CANDIDATE and lives in
  `metadata` (e.g. `attack_candidates`) as a hypothesis, never presented as confirmed.

N3 / tool-retrieval scenarios:
- `retrievable_events` holds telemetry that a (future) read-only tool layer would
  return; it is NOT part of the initial alert context handed to triage.
- `initial_context_disposition` is the reference triage decision on the initial
  context ALONE. It is a methodologically CHOSEN reference, not a dataset-provided
  fact.
- `requires_tool_retrieval=True` marks the scenario as NOT end-to-end runnable until
  a tool-execution step (Baseline D) exists.
"""

from __future__ import annotations

from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from sentinelx.schemas.alert import RawAlert
from sentinelx.schemas.enums import Disposition
from sentinelx.schemas.event import Event


class Scenario(BaseModel):
    """A labeled investigation scenario used as evaluation ground truth."""

    # Strict: reject any field we did not declare. Catches typos in scenario files
    # (e.g. "expected_tecnhiques") instead of silently ignoring them.
    model_config = ConfigDict(extra="forbid")

    # --- Identity (required) ---
    scenario_id: str = Field(
        ..., min_length=1, description="Stable, non-empty id, e.g. 'SC-BRUTEFORCE-001'."
    )
    description: str = Field(..., description="What this scenario represents, in plain words.")

    # --- Input (required) ---
    # The alert under investigation. Reuses the existing RawAlert contract, which
    # already carries its telemetry events. No duplication of the alert/event shape.
    alert: RawAlert

    # --- Core ground truth (required) ---
    expected_disposition: Disposition = Field(
        ..., description="Reference triage decision (escalate / dismiss / insufficient_evidence)."
    )
    reference_conclusion: str = Field(
        ..., description="The 'gold' conclusion a correct investigation should reach."
    )

    # --- Rich ground truth (optional; safe empty defaults) ---
    acceptable_conclusions: list[str] = Field(
        default_factory=list,
        description="Other conclusions that should also be accepted as correct.",
    )
    expected_techniques: list[str] = Field(
        default_factory=list,
        description=(
            "MITRE ATT&CK technique ids ESTABLISHED by this scenario (see module "
            "docstring for the canonical synthetic-vs-real rule). Candidate/hypothesis "
            "techniques do NOT go here; they belong in metadata.attack_candidates."
        ),
    )
    key_evidence_event_ids: list[str] = Field(
        default_factory=list,
        description="Ids of the decisive events; each must exist in alert.events OR retrievable_events.",
    )
    expected_unknowns: list[str] = Field(
        default_factory=list,
        description="Facts that must stay unknown ('insufficient evidence') given the data.",
    )

    # --- Policy ground truth (optional; for later tool/policy evaluation) ---
    allowed_actions: list[str] = Field(
        default_factory=list, description="Read-only actions permitted for this scenario."
    )
    forbidden_actions: list[str] = Field(
        default_factory=list, description="Actions that must never be taken."
    )

    # --- N3 / tool-retrieval ground truth (optional; safe defaults) ---
    retrievable_events: list[Event] = Field(
        default_factory=list,
        description=(
            "Telemetry a (future) read-only tool layer would return. NOT part of the "
            "initial alert context; never fed to tool-less baselines. Ids must be "
            "disjoint from alert.events."
        ),
    )
    initial_context_disposition: Disposition | None = Field(
        default=None,
        description=(
            "Reference triage decision on the INITIAL context alone (trigger + "
            "distractors, no retrievable_events). A chosen methodological reference, "
            "not a dataset-provided fact. Set it for tool-retrieval scenarios."
        ),
    )
    requires_tool_retrieval: bool = Field(
        default=False,
        description=(
            "True marks the scenario as NOT end-to-end runnable until a tool-execution "
            "step (Baseline D) exists. The decisive evidence lives in retrievable_events."
        ),
    )

    # --- Metadata (optional) ---
    tags: list[str] = Field(default_factory=list, description="Labels, e.g. 'brute-force'.")
    metadata: dict[str, str] = Field(
        default_factory=dict, description="Free-form provenance / author notes."
    )

    @model_validator(mode="after")
    def _event_ids_are_consistent(self) -> Self:
        """Validate event-id consistency across the initial and retrievable sets.

        Runs AFTER the model is built (mode="after"), so `self.alert` is a validated
        RawAlert. Two guarantees, the scenario-side analogue of the report citation
        check (no reference to evidence that does not exist):

        1. No id collision between `alert.events` (initial context) and
           `retrievable_events` (tool-returnable) — a single event must not live in both.
        2. Every id in `key_evidence_event_ids` matches a real event in EITHER set.

        This validates ID CONSISTENCY ONLY. It does NOT (and cannot) verify that a
        future tool layer will actually return the retrievable_events — that capability
        is deferred (Baseline D).
        """
        initial_ids = {event.id for event in self.alert.events}
        retrievable_ids = {event.id for event in self.retrievable_events}

        collisions = initial_ids & retrievable_ids
        if collisions:
            raise ValueError(
                "event id(s) appear in BOTH alert.events and retrievable_events: "
                f"{sorted(collisions)}. An event belongs to one set only."
            )

        known_event_ids = initial_ids | retrievable_ids
        dangling = [
            eid for eid in self.key_evidence_event_ids if eid not in known_event_ids
        ]
        if dangling:
            raise ValueError(
                "key_evidence_event_ids references event id(s) absent from the scenario: "
                f"{dangling}. Known event ids (alert + retrievable): {sorted(known_event_ids)}."
            )
        return self