"""Schema validation contracts."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from sentinelx.schemas import (
    Citation,
    Disposition,
    Finding,
    FindingKind,
    InvestigationReport,
    RawAlert,
)


def test_raw_alert_allows_extra_but_requires_core():
    alert = RawAlert.model_validate(
        {
            "id": "A1",
            "source": "wazuh",
            "timestamp": "2026-10-17T08:00:00Z",
            "title": "t",
            "vendor_specific": {"x": 1},  # extra allowed
        }
    )
    assert alert.id == "A1"


def test_raw_alert_missing_required_field_fails():
    with pytest.raises(ValidationError):
        RawAlert.model_validate({"source": "wazuh", "timestamp": "2026-10-17T08:00:00Z"})


def test_fact_requires_citation():
    with pytest.raises(ValidationError):
        Finding(kind=FindingKind.FACT, statement="something happened", citations=[])


def test_hypothesis_without_citation_is_allowed():
    f = Finding(kind=FindingKind.HYPOTHESIS, statement="maybe brute force")
    assert f.citations == []


def test_report_forbids_unknown_fields():
    with pytest.raises(ValidationError):
        InvestigationReport.model_validate(
            {
                "alert_id": "A1",
                "disposition": Disposition.DISMISS.value,
                "summary": "s",
                "unexpected": True,
            }
        )


def test_fact_with_citation_builds():
    f = Finding(
        kind=FindingKind.FACT,
        statement="observed",
        citations=[Citation(evidence_id="EV-EVENT-1")],
    )
    assert f.citations[0].evidence_id == "EV-EVENT-1"
