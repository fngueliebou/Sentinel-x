"""End-to-end pipeline: raw alert -> normalized -> (RAG) -> analysis -> verified report."""

from __future__ import annotations

from pathlib import Path

from sentinelx.config import Settings, load_settings
from sentinelx.ingestion import load_raw_alert, load_raw_alert_from_dict
from sentinelx.knowledge import InMemoryKnowledgeStore, load_sample_store
from sentinelx.llm import get_provider
from sentinelx.normalization import normalize_alert
from sentinelx.schemas import InvestigationReport, RawAlert
from sentinelx.investigation import investigate


def run_investigation(
    raw: RawAlert,
    *,
    settings: Settings | None = None,
    store: InMemoryKnowledgeStore | None = None,
    use_rag: bool = True,
) -> InvestigationReport:
    """Run the full slice on an already-loaded RawAlert."""
    settings = settings or load_settings()
    provider = get_provider(settings)
    if use_rag and store is None:
        store = load_sample_store()
    normalized = normalize_alert(raw)
    return investigate(
        normalized,
        provider=provider,
        store=store,
        use_rag=use_rag,
        top_k=settings.retrieval_top_k,
    )


def run_investigation_from_file(
    path: str | Path,
    *,
    settings: Settings | None = None,
    use_rag: bool = True,
) -> InvestigationReport:
    return run_investigation(load_raw_alert(path), settings=settings, use_rag=use_rag)


def run_investigation_from_dict(
    payload: dict,
    *,
    settings: Settings | None = None,
    use_rag: bool = True,
) -> InvestigationReport:
    return run_investigation(load_raw_alert_from_dict(payload), settings=settings, use_rag=use_rag)
