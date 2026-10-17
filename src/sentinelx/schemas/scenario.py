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
  events that actually exist in the alert — the same "no dangling reference"
  principle the citation verifier enforces for reports.
"""

from __future__ import annotations

from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from sentinelx.schemas.alert import RawAlert
from sentinelx.schemas.enums import Disposition


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
        description="MITRE ATT&CK technique ids expected, e.g. 'T1110'. Free-form on purpose.",
    )
    key_evidence_event_ids: list[str] = Field(
        default_factory=list,
        description="Ids of the decisive events; each must exist in alert.events.",
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

    # --- Metadata (optional) ---
    tags: list[str] = Field(default_factory=list, description="Labels, e.g. 'brute-force'.")
    metadata: dict[str, str] = Field(
        default_factory=dict, description="Free-form provenance / author notes."
    )

    @model_validator(mode="after")
    def _key_evidence_refers_to_real_events(self) -> Self:
        """Every id in key_evidence_event_ids must match an event in the alert.

        Runs AFTER the model is built (mode="after"), so `self.alert` is already a
        validated RawAlert and we can read its events. This is the scenario-side
        analogue of the report citation check: no reference to evidence that does
        not exist.
        """
        known_event_ids = {event.id for event in self.alert.events}
        dangling = [
            eid for eid in self.key_evidence_event_ids if eid not in known_event_ids
        ]
        if dangling:
            raise ValueError(
                "key_evidence_event_ids references event id(s) absent from the alert: "
                f"{dangling}. Known event ids: {sorted(known_event_ids)}."
            )
        return self