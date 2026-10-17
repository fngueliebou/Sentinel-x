"""Investigation orchestration.

Assembles the evidence set (events [+ retrieved knowledge]), calls the provider,
assembles an InvestigationReport, then runs verification. `use_rag=False` yields
the LLM-only ablation (Baseline B); `use_rag=True` yields LLM+RAG (Baseline C)
and the fuller pipeline.
"""

from __future__ import annotations

from sentinelx.investigation.evidence_builder import build_event_evidence
from sentinelx.investigation.prompt import PROMPT_VERSION
from sentinelx.knowledge.base import KnowledgeStore
from sentinelx.llm.base import AnalysisRequest, LLMProvider
from sentinelx.rag.retriever import retrieve_knowledge
from sentinelx.schemas import Evidence, InvestigationReport, NormalizedAlert
from sentinelx.verification.verifier import verify_report


def investigate(
    alert: NormalizedAlert,
    provider: LLMProvider,
    store: KnowledgeStore | None = None,
    *,
    use_rag: bool = True,
    top_k: int = 5,
) -> InvestigationReport:
    evidence: list[Evidence] = build_event_evidence(alert)

    if use_rag:
        if store is None:
            raise ValueError("use_rag=True requires a knowledge store.")
        evidence = evidence + retrieve_knowledge(alert, store, top_k=top_k)

    output = provider.analyze(
        AnalysisRequest(alert=alert, evidence=evidence, prompt_version=PROMPT_VERSION)
    )

    report = InvestigationReport(
        alert_id=alert.id,
        disposition=output.disposition,
        summary=output.summary,
        facts=output.facts,
        hypotheses=output.hypotheses,
        unknowns=output.unknowns,
        recommendations=output.recommendations,
        evidence=evidence,
        llm_provider=provider.name,
        llm_model=output.model,
        prompt_version=PROMPT_VERSION,
    )

    return verify_report(report)
