"""Investigation report contract.

The report separates facts / hypotheses / unknowns / recommendations and carries
the evidence set it was built from. A FACT with no valid citation is a contract
violation that the verifier flags (conception v0.2 §3; EVALUATION.md §7.b).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from sentinelx.schemas.enums import Disposition, FindingKind
from sentinelx.schemas.evidence import Citation, Evidence


class Finding(BaseModel):
    """One statement in the report, typed by FindingKind."""

    model_config = ConfigDict(extra="forbid")

    kind: FindingKind
    statement: str
    citations: list[Citation] = Field(default_factory=list)
    # Set by the verifier; None until verification runs.
    supported: bool | None = Field(
        default=None, description="True if every citation resolves to a real evidence id."
    )

    @model_validator(mode="after")
    def _facts_cite_something(self) -> Self:
        # A FACT must carry at least one citation (validity of the id is checked
        # later by the verifier against the actual evidence set).
        if self.kind == FindingKind.FACT and not self.citations:
            raise ValueError("A FACT finding must have at least one citation.")
        return self


class TriageDecision(BaseModel):
    """Deterministic/triage output; also embedded in the report header."""

    model_config = ConfigDict(extra="forbid")

    disposition: Disposition
    priority: int = Field(..., ge=0, le=100, description="0 = lowest, 100 = highest.")
    rationale: str
    matched_rules: list[str] = Field(default_factory=list)


class InvestigationReport(BaseModel):
    """The structured output of an investigation."""

    model_config = ConfigDict(extra="forbid")

    alert_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    disposition: Disposition
    summary: str

    facts: list[Finding] = Field(default_factory=list)
    hypotheses: list[Finding] = Field(default_factory=list)
    unknowns: list[Finding] = Field(default_factory=list)
    recommendations: list[Finding] = Field(default_factory=list)

    evidence: list[Evidence] = Field(
        default_factory=list, description="The evidence set the report was built from."
    )

    # Provenance / reproducibility (conception §8).
    llm_provider: str = "unknown"
    llm_model: str | None = None
    prompt_version: str = "unknown"

    # Set by the verifier.
    verification_passed: bool | None = None
    verification_notes: list[str] = Field(default_factory=list)

    def evidence_ids(self) -> set[str]:
        return {e.id for e in self.evidence}
