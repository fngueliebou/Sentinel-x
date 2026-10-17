"""Citation verification: facts must cite real evidence; fabricated ids are caught."""

from __future__ import annotations

from sentinelx.schemas import (
    Citation,
    Disposition,
    Evidence,
    Finding,
    FindingKind,
    InvestigationReport,
    SourceType,
)
from sentinelx.verification import verify_report


def _evidence(ev_id: str) -> Evidence:
    return Evidence(
        id=ev_id,
        source_type=SourceType.EVENT,
        source_ref="event:e1",
        content="Failed password for jdoe",
    )


def test_valid_citation_passes():
    report = InvestigationReport(
        alert_id="A1",
        disposition=Disposition.ESCALATE,
        summary="s",
        facts=[
            Finding(
                kind=FindingKind.FACT,
                statement="observed failure",
                citations=[Citation(evidence_id="EV-EVENT-1")],
            )
        ],
        evidence=[_evidence("EV-EVENT-1")],
    )
    verified = verify_report(report)
    assert verified.verification_passed is True
    assert verified.facts[0].supported is True


def test_fabricated_citation_is_flagged():
    report = InvestigationReport(
        alert_id="A1",
        disposition=Disposition.ESCALATE,
        summary="s",
        facts=[
            Finding(
                kind=FindingKind.FACT,
                statement="hallucinated claim",
                citations=[Citation(evidence_id="EV-DOES-NOT-EXIST")],
            )
        ],
        evidence=[_evidence("EV-EVENT-1")],
    )
    verified = verify_report(report)
    assert verified.verification_passed is False
    assert verified.facts[0].supported is False
    assert any("not found" in n for n in verified.verification_notes)
