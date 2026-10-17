"""RAG retrieval and provenance."""

from __future__ import annotations

from sentinelx.ingestion import load_raw_alert
from sentinelx.normalization import normalize_alert
from sentinelx.rag import retrieve_knowledge
from sentinelx.schemas import SourceType


def test_retrieval_returns_knowledge_with_provenance(store):
    alert = normalize_alert(load_raw_alert("data/alerts/sample_alert_bruteforce.json"))
    evidence = retrieve_knowledge(alert, store, top_k=5)
    assert evidence, "expected at least one knowledge hit for a brute-force alert"
    for ev in evidence:
        assert ev.source_type == SourceType.KNOWLEDGE
        assert ev.source_ref  # provenance preserved
        assert ev.source_version  # versioned knowledge
        assert ev.score is not None


def test_brute_force_retrieves_t1110(store):
    alert = normalize_alert(load_raw_alert("data/alerts/sample_alert_bruteforce.json"))
    refs = {e.source_ref for e in retrieve_knowledge(alert, store, top_k=5)}
    assert any("T1110" in r for r in refs)


def test_empty_query_returns_nothing(store):
    assert store.search("", top_k=5) == []
