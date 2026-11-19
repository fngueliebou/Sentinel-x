"""Investigation scenario contract (ground truth for evaluation).

A Scenario wraps an input alert together with the ground truth an investigation
should recover: the reference conclusion, the techniques, the decisive evidence,
what must stay unknown, and the actions that are / are not allowed. It is what
lets us evaluate an investigation, not merely a triage label.

Design choices:
- The alert is embedded as a `RawAlert` (composition), not re-declared, so there
  is a single source of truth for the alert/event shape (schemas/alert.py).
- Strict validation (`extra="forbid"`) matches the other output-side schemas, so
  a malformed scenario fails fast instead of silently carrying junk.
- A cross-field validator guarantees that `key_evidence_event_ids` only names
  events that actually exist (in the initial alert OR the retrievable set) — the
  same "no dangling reference" principle the citation verifier enforces.
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
            "MITRE ATT&CK technique ids establish by this scenario (see module "
            "docstring for the canonical synthetic-vs-real rule). Candidate/hypothesis "
            "techniques do not go here; they belong in metadata.attack_candidates."
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
            "Telemetry a (future) read-only tool layer would return. Not part of the "
            "initial alert context; never fed to tool-less baselines. Ids must be "
            "disjoint from alert.events."
        ),
    )
    initial_context_disposition: Disposition | None = Field(
        default=None,
        description=(
            "Reference triage decision on the initial context alone (trigger + "
            "distractors, no retrievable_events). A chosen methodological reference, "
            "not a dataset-provided fact. Set it for tool-retrieval scenarios."
        ),
    )
    requires_tool_retrieval: bool = Field(
        default=False,
        description=(
            "True marks the scenario as not end-to-end runnable until a tool-execution "
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
        """Validate event-id consistency across the initial and retrievable sets"""
        initial_ids = {event.id for event in self.alert.events}
        retrievable_ids = {event.id for event in self.retrievable_events}

        collisions = initial_ids & retrievable_ids
        if collisions:
            raise ValueError(
                "event id(s) appear in both alert.events and retrievable_events: "
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