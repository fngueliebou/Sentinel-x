"""End-to-end pipeline, including the RAG ablation (Baseline B vs C)."""

from __future__ import annotations

from sentinelx.pipeline import run_investigation_from_file
from sentinelx.schemas import Disposition, FindingKind


def test_e2e_bruteforce_produces_verified_grounded_report(settings):
    report = run_investigation_from_file(
        "data/alerts/sample_alert_bruteforce.json", settings=settings
    )
    assert report.disposition == Disposition.ESCALATE
    assert report.verification_passed is True
    # Every fact must be supported and cite a real evidence id.
    assert report.facts
    for fact in report.facts:
        assert fact.kind == FindingKind.FACT
        assert fact.supported is True
        assert fact.citations
        for c in fact.citations:
            assert c.evidence_id in report.evidence_ids()


def test_e2e_report_has_all_sections_shape(settings):
    report = run_investigation_from_file(
        "data/alerts/sample_alert_bruteforce.json", settings=settings
    )
    # facts/hypotheses/unknowns/recommendations are present as lists.
    assert isinstance(report.facts, list)
    assert isinstance(report.hypotheses, list)
    assert isinstance(report.unknowns, list)
    assert isinstance(report.recommendations, list)
    assert report.prompt_version
    assert report.llm_provider == "deterministic"


def test_rag_ablation_adds_hypotheses(settings):
    # Baseline B (no RAG): no knowledge evidence -> no knowledge-grounded hypotheses.
    b = run_investigation_from_file(
        "data/alerts/sample_alert_bruteforce.json", settings=settings, use_rag=False
    )
    # Baseline C (RAG): knowledge retrieved -> hypotheses grounded in knowledge.
    c = run_investigation_from_file(
        "data/alerts/sample_alert_bruteforce.json", settings=settings, use_rag=True
    )
    assert len(b.hypotheses) == 0
    assert len(c.hypotheses) >= 1
    # Disposition is driven by structured signal, so it is stable across the ablation.
    assert b.disposition == c.disposition == Disposition.ESCALATE


def test_insufficient_evidence_is_expressible(settings):
    report = run_investigation_from_file(
        "data/alerts/sample_alert_ambiguous.json", settings=settings
    )
    assert report.disposition == Disposition.INSUFFICIENT_EVIDENCE
    assert report.verification_passed is True
