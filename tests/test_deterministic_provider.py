"""Non-regression tests for the deterministic provider's recommendations"""

from __future__ import annotations

from collections import Counter

from sentinelx.pipeline import run_investigation_from_file

_BRUTEFORCE = "data/alerts/sample_alert_bruteforce.json"
_SCANNER_REC = "approved-scanner inventory"


def test_no_duplicate_recommendations(settings):
    report = run_investigation_from_file(_BRUTEFORCE, settings=settings)
    statements = [rec.statement for rec in report.recommendations]
    duplicates = [s for s, count in Counter(statements).items() if count > 1]
    assert not duplicates, f"duplicate recommendations found: {duplicates}"


def test_scanner_check_recommended_once_and_cites_runbook(settings):
    report = run_investigation_from_file(_BRUTEFORCE, settings=settings)
    scanner_recs = [r for r in report.recommendations if _SCANNER_REC in r.statement]

    # Exactly one scanner-check recommendation, not two.
    assert len(scanner_recs) == 1

    # It must cite the scanner runbook (the only scanner-specific knowledge), not
    # an unrelated technique whose text happened to contain the word "benign".
    cited_ids = {c.evidence_id for c in scanner_recs[0].citations}
    cited_evidence = [e for e in report.evidence if e.id in cited_ids]
    assert any("RB-FP-SCANNER" in e.source_ref for e in cited_evidence)