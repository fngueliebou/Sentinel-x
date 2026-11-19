"""Contract + end-to-end run test: fox-dnsteal-dns-exfil.

Two concerns, kept separate:

1. The scenario is a well-formed, internally consistent artifact grounded in the
   AIT-ADS 'dnsteal' window (schema validity, honest-conclusion invariants,
   no fabricated ATT&CK mapping).
2. The existing pipeline runs on it with the deterministic provider (Baseline B)
   and its observed behavior is recorded.
"""

from __future__ import annotations

import json
from pathlib import Path

from sentinelx.config import Settings
from sentinelx.pipeline import run_investigation
from sentinelx.schemas import Disposition, Scenario, SourceType

_SCENARIO = Path("data/scenarios/scenario_fox_dnsteal.json")
# Pin the deterministic provider so these tests never depend on the ambient
# environment / a local .env (reproducibility). Explicit Settings kwargs take
# precedence over env and .env in pydantic-settings.
_DETERMINISTIC = Settings(llm_provider="deterministic")


def _scenario() -> Scenario:
    return Scenario.model_validate(json.loads(_SCENARIO.read_text(encoding="utf-8")))


# --- 1. Artifact-level invariants (no pipeline) ---------------------------------

def test_scenario_loads_and_is_consistent():
    sc = _scenario()
    assert sc.scenario_id == "fox-dnsteal-dns-exfil"
    assert len(sc.alert.events) == 10
    # The model_validator already guarantees key evidence ids are real events;
    # assert the intended selection explicitly (signal + context, not the noise).
    assert set(sc.key_evidence_event_ids) == {"e1", "e2", "e3", "e4", "e6"}


def test_disposition_is_escalate_for_investigation():
    sc = _scenario()
    # Escalation for investigation, not a conclusion that exfiltration occurred.
    assert sc.expected_disposition is Disposition.ESCALATE


def test_no_fabricated_attack_mapping():
    sc = _scenario()
    # Honesty invariant: nothing is confirmed from this telemetry, so the flat
    # expected_techniques list stays empty; candidates live in metadata as
    # hypotheses. This guards against someone later asserting DNS exfil as fact.
    assert sc.expected_techniques == []
    assert "HYPOTHESES" in sc.metadata["attack_candidates"]


def test_curated_subset_is_documented_not_full_window():
    sc = _scenario()
    # The subset must never be mistaken for the full 381-alert window.
    comp = sc.metadata["window_composition"]
    assert "381" in comp and "336" in comp
    assert "CURATED SUBSET" in comp


def test_benign_dovecot_is_not_key_evidence():
    sc = _scenario()
    dovecot_ids = {
        e.id for e in sc.alert.events if e.attributes.get("rule_id") == "9701"
    }
    assert dovecot_ids  # sanity: the benign noise is present in the subset
    assert dovecot_ids.isdisjoint(set(sc.key_evidence_event_ids))


def test_dns_and_tls_are_on_distinct_hosts():
    sc = _scenario()
    # The honesty of the scenario rests on NOT conflating these two hosts.
    e1 = next(e for e in sc.alert.events if e.id == "e1")
    e3 = next(e for e in sc.alert.events if e.id == "e3")
    assert e1.attributes["src_ip"] == "172.17.130.196"   # DNS .cloud query source
    assert e3.attributes["dest_ip"] == "192.168.128.4"   # TLS anomaly internal host
    assert e1.attributes["src_ip"] != e3.attributes["dest_ip"]


# --- 2. Pipeline run (Baseline B, deterministic, no RAG, no network) ------------

def _run():
    sc = _scenario()
    report = run_investigation(sc.alert, use_rag=False, settings=_DETERMINISTIC)
    return sc, report


def test_pipeline_runs_baseline_b_deterministic_no_rag():
    _sc, report = _run()
    assert report.llm_provider == "deterministic"
    # No RAG -> every evidence item is an event; no retrieved knowledge/hypotheses.
    assert all(e.source_type is SourceType.EVENT for e in report.evidence)
    assert report.hypotheses == []


def test_citations_are_valid():
    _sc, report = _run()
    assert report.verification_passed is True
    evidence_ids = report.evidence_ids()
    for f in report.facts:
        assert f.citations
        assert f.supported is True
        assert all(c.evidence_id in evidence_ids for c in f.citations)


def test_expected_gap_stub_does_not_reach_escalate():
    sc, report = _run()

    assert sc.expected_disposition is Disposition.ESCALATE
    assert report.disposition is Disposition.INSUFFICIENT_EVIDENCE
    assert report.disposition != sc.expected_disposition


def test_expected_unknowns_present_in_scenario_absent_in_stub():
    sc, report = _run()
    assert sc.expected_unknowns
    assert report.unknowns == []