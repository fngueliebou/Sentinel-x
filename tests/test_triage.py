"""Deterministic triage baseline (Baseline A)."""

from __future__ import annotations

from sentinelx.ingestion import load_raw_alert
from sentinelx.normalization import normalize_alert
from sentinelx.schemas import Disposition
from sentinelx.triage import triage


def _triage_file(path):
    return triage(normalize_alert(load_raw_alert(path)))


def test_bruteforce_escalates():
    d = _triage_file("data/alerts/sample_alert_bruteforce.json")
    assert d.disposition == Disposition.ESCALATE
    assert d.priority >= 80
    assert d.matched_rules


def test_ambiguous_is_insufficient_evidence():
    d = _triage_file("data/alerts/sample_alert_ambiguous.json")
    assert d.disposition == Disposition.INSUFFICIENT_EVIDENCE


def test_no_events_is_insufficient_evidence():
    from sentinelx.ingestion import load_raw_alert_from_dict

    raw = load_raw_alert_from_dict(
        {
            "id": "A9",
            "source": "x",
            "timestamp": "2026-10-17T08:00:00Z",
            "title": "no telemetry",
            "severity": "high",
            "events": [],
        }
    )
    d = triage(normalize_alert(raw))
    assert d.disposition == Disposition.INSUFFICIENT_EVIDENCE
