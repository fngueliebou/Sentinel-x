"""Investigation orchestration: assemble evidence, call the provider, build report."""

from sentinelx.investigation.prompt import PROMPT_VERSION
from sentinelx.investigation.evidence_builder import build_event_evidence
from sentinelx.investigation.investigator import investigate

__all__ = ["PROMPT_VERSION", "build_event_evidence", "investigate"]
