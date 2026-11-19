"""RAG coverage test for the fox-privesc-shadow case.

Verifies that, through the real pipeline query path (normalize_alert -> build_query
inside retrieve_knowledge), the two newly added ATT&CK cards (T1548.003 and
T1003.008) are among the retrieved documents for this scenario
"""

from __future__ import annotations

import json
from pathlib import Path

from sentinelx.knowledge import load_sample_store
from sentinelx.normalization import normalize_alert
from sentinelx.rag.retriever import retrieve_knowledge
from sentinelx.schemas import Scenario

_SCENARIO = Path("data/scenarios/scenario_fox_privesc_shadow.json")
_TOP_K = 5


def _scenario() -> Scenario:
    return Scenario.model_validate(json.loads(_SCENARIO.read_text(encoding="utf-8")))


def test_new_cards_present_in_sample_store():
    refs = {doc.source_ref for doc in load_sample_store().all_documents()}
    assert "T1548.003" in refs
    assert "T1003.008" in refs


def test_privesc_retrieval_covers_sudo_and_shadow_cards():
    normalized = normalize_alert(_scenario().alert)
    evidence = retrieve_knowledge(normalized, load_sample_store(), top_k=_TOP_K)

    assert len(evidence) == _TOP_K  # more than top_k docs overlap -> exactly top_k returned
    refs = " ".join(e.source_ref for e in evidence)
    # Both newly added cards are retrieved for this scenario (coverage closed).
    assert "T1548.003" in refs  # sudo privilege-escalation
    assert "T1003.008" in refs  # /etc/passwd and /etc/shadow credential access