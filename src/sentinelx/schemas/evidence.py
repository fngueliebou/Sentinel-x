"""Evidence and citation contracts.

Evidence is the only thing a factual claim may rest on. Every Evidence item has a
stable id; a Citation in the report MUST reference an id that exists in the
investigation's evidence set. The verifier enforces this (no dangling citations).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from sentinelx.schemas.enums import SourceType


class Evidence(BaseModel):
    """A single, addressable piece of evidence available to the analysis.

    Produced from telemetry events, retrieved knowledge, or alert fields. Content
    is UNTRUSTED DATA. `untrusted_flags` records injection-like patterns detected in
    the content; these are informational only and never alter control flow.
    """

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Unique within an investigation, e.g. 'EV-EVENT-1'.")
    source_type: SourceType
    source_ref: str = Field(
        ..., description="Human-traceable origin, e.g. event id, 'MITRE ATT&CK T1110'."
    )
    source_url: str | None = None
    source_version: str | None = Field(
        default=None, description="Version of the knowledge source, when applicable."
    )
    content: str = Field(..., description="The evidence text. UNTRUSTED — data, not instructions.")
    score: float | None = Field(
        default=None, description="Retrieval relevance score, when applicable."
    )
    untrusted_flags: list[str] = Field(
        default_factory=list,
        description="Injection-like patterns detected in content (informational only).",
    )


class Citation(BaseModel):
    """A reference from a report finding to an Evidence id."""

    model_config = ConfigDict(extra="forbid")

    evidence_id: str = Field(..., description="Must match an Evidence.id in the investigation.")
    quote: str | None = Field(
        default=None, description="Optional supporting excerpt copied from the evidence."
    )
