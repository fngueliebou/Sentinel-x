"""Normalization behavior."""

from __future__ import annotations

from sentinelx.ingestion import load_raw_alert_from_dict
from sentinelx.normalization import normalize_alert
from sentinelx.schemas import Severity


def _raw(severity, with_events=True):
    payload = {
        "id": "A1",
        "source": "wazuh",
        "timestamp": "2026-10-17T08:00:00Z",
        "title": "t",
        "severity": severity,
        "entities": ["user:x"],
        "events": (
            [
                {
                    "id": "e1",
                    "timestamp": "2026-10-17T08:00:00Z",
                    "source": "auth",
                    "action": "login_failed",
                    "message": "Failed password",
                }
            ]
            if with_events
            else []
        ),
    }
    return load_raw_alert_from_dict(payload)


def test_severity_mapping_known_label():
    assert normalize_alert(_raw("high")).severity == Severity.HIGH


def test_severity_numeric_bucketing():
    assert normalize_alert(_raw("12")).severity == Severity.CRITICAL


def test_unknown_severity_defaults_and_is_flagged_missing():
    n = normalize_alert(_raw("weird-label"))
    assert n.severity == Severity.MEDIUM
    assert "severity" in n.missing_fields


def test_missing_severity_is_flagged():
    n = normalize_alert(_raw(None))
    assert "severity" in n.missing_fields


def test_missing_events_flagged():
    n = normalize_alert(_raw("low", with_events=False))
    assert "events" in n.missing_fields
