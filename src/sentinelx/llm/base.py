"""LLM provider interface and request/response contracts."""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from sentinelx.schemas import Disposition, Evidence, Finding, NormalizedAlert


class AnalysisRequest(BaseModel):
    """Everything a provider needs to analyze one alert"""

    model_config = ConfigDict(extra="forbid")

    alert: NormalizedAlert
    evidence: list[Evidence]
    prompt_version: str


class ProviderUsage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = Field(
        default=None, description="Estimated cost; None when not applicable (e.g. offline)."
    )


class ProviderOutput(BaseModel):
    """Structured analysis returned by a provider (before verification)."""

    model_config = ConfigDict(extra="forbid")

    disposition: Disposition
    summary: str
    facts: list[Finding] = Field(default_factory=list)
    hypotheses: list[Finding] = Field(default_factory=list)
    unknowns: list[Finding] = Field(default_factory=list)
    recommendations: list[Finding] = Field(default_factory=list)
    model: str | None = None
    usage: ProviderUsage | None = None


class LLMProvider(Protocol):
    name: str

    def analyze(self, request: AnalysisRequest) -> ProviderOutput:
        ...
