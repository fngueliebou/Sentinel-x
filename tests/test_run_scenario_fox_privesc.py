"""End-to-end run test: fox-privesc-shadow through the deterministic pipeline (Baseline B).

Exercises exactly what scripts/run_scenario.py drives: load the Scenario, run the
EXISTING pipeline on scenario.alert with the deterministic provider and NO RAG, then
check loading, execution, report structure, citation validity, and the EXPECTED gaps
between the rule-based stub and the scenario's ground truth.

Assertions reflect the pipeline's OBSERVED behavior (the run was executed before the
assertions were written), not a prediction. This is a technical validation of the
pipeline and of the stub's limits - NOT a performance measurement, NOT an LLM
evaluation, and NOT a validation of the AIT-ADS time_label as certain ground truth.
"""

from __future__ import annotations

import json
from pathlib import Path

from sentinelx.pipeline import run_investigation
from sentinelx.schemas import Disposition, Scenario, SourceType

_SCENARIO = Path("data/scenarios/scenario_fox_privesc_shadow.json")


def _scenario() -> Scenario:
    return Scenario.model_validate(json.loads(_SCENARIO.read_text(encoding="utf-8")))


def _run():
    sc = _scenario()
    # Baseline B: deterministic provider, NO retrieval (no API, no network).
    report = run_investigation(sc.alert, use_rag=False)
    return sc, report


def test_scenario_loads():
    sc = _scenario()
    assert sc.scenario_id == "fox-privesc-shadow"
    assert len(sc.alert.events) == 10


def test_pipeline_runs_baseline_b_deterministic_no_rag():
    _sc, report = _run()
    assert report.llm_provider == "deterministic"
    # No RAG -> every evidence item is an EVENT; no retrieved KNOWLEDGE, no hypotheses.
    assert all(e.source_type is SourceType.EVENT for e in report.evidence)
    assert report.hypotheses == []


def test_report_structure_and_citation_validity():
    _sc, report = _run()
    # Independent citation check passed: no FACT cites a non-existent evidence id.
    assert report.verification_passed is True
    evidence_ids = report.evidence_ids()
    for f in report.facts:
        assert f.citations              # a FACT must cite something
        assert f.supported is True      # and the verifier confirmed it
        assert all(c.evidence_id in evidence_ids for c in f.citations)
    # Observed: one grounded fact per telemetry event (no failed-auth aggregate here).
    assert len(report.facts) == len(report.evidence)


def test_key_evidence_is_grounded_in_supported_facts():
    sc, report = _run()
    supported_citations = {
        c.evidence_id for f in report.facts if f.supported for c in f.citations
    }
    for eid in sc.key_evidence_event_ids:
        matches = [e for e in report.evidence if e.source_ref == f"event:{eid}"]
        assert len(matches) == 1, f"key evidence {eid} not found exactly once in evidence set"
        assert matches[0].id in supported_citations


def test_expected_gaps_are_observed():
    sc, report = _run()
    # Disposition gap: the brute-force stub cannot reach the reference ESCALATE on a
    # privilege-escalation chain (no failed-auth events to count).
    assert sc.expected_disposition is Disposition.ESCALATE
    assert report.disposition is Disposition.INSUFFICIENT_EVIDENCE
    assert report.disposition != sc.expected_disposition
    # Unknowns gap: the scenario documents legitimate unknowns; the stub emits none.
    # Absence in the report is a STUB limitation, NOT an absence from the data.
    assert sc.expected_unknowns
    assert report.unknowns == []


def _run_c():
    sc = _scenario()
    # Baseline C: deterministic provider WITH RAG over the sample store (still no API).
    report = run_investigation(sc.alert, use_rag=True)
    return sc, report


def test_baseline_c_runs_and_retrieves_knowledge():
    _sc, report = _run_c()
    assert report.llm_provider == "deterministic"
    assert report.verification_passed is True
    kb = [e for e in report.evidence if e.source_type is SourceType.KNOWLEDGE]
    events = [e for e in report.evidence if e.source_type is SourceType.EVENT]
    # RAG retrieved knowledge (exact count depends on the KB; assert presence, not a number).
    assert len(kb) >= 1
    assert len(events) == 10  # the telemetry events are still all present


def test_baseline_c_hypotheses_cite_retrieved_knowledge():
    _sc, report = _run_c()
    evidence_ids = report.evidence_ids()
    assert report.hypotheses  # RAG produced at least one hypothesis
    for h in report.hypotheses:
        assert h.citations
        assert all(c.evidence_id in evidence_ids for c in h.citations)
        assert h.supported is True


def test_rag_does_not_change_deterministic_disposition():
    sc = _scenario()
    report_b = run_investigation(sc.alert, use_rag=False)
    report_c = run_investigation(sc.alert, use_rag=True)
    # The deterministic provider derives its disposition from structured signals only,
    # never from retrieved knowledge -> RAG leaves the triage decision unchanged here.
    assert report_c.disposition == report_b.disposition