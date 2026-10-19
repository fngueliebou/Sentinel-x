"""Tests for the AIT-ADS Wazuh loader (sentinelx.datasets.ait_ads).

Runs against a tiny committed fixture of real Wazuh records (first 3 lines of
fox_wazuh.json), so it is fast and never touches the multi-hundred-MB files.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from sentinelx.datasets.ait_ads import iter_wazuh_alerts, wazuh_record_to_raw_alert

_SAMPLE = Path(__file__).resolve().parent / "data" / "ait_ads" / "fox_wazuh.sample.jsonl"


def test_sample_fixture_exists():
    assert _SAMPLE.is_file()


def test_iter_reads_every_record():
    alerts = list(iter_wazuh_alerts(_SAMPLE))
    assert len(alerts) == 3
    assert all(a.source == "wazuh" for a in alerts)


def test_first_record_is_mapped_correctly():
    first = next(iter_wazuh_alerts(_SAMPLE))
    assert first.id == "1686147193.86593"
    assert first.source == "wazuh"
    assert first.timestamp == datetime(2022, 1, 15, 2, 32, 32, tzinfo=timezone.utc)
    assert first.title == "ClamAV database update"
    assert first.severity == "3"  # rule.level kept as a raw string, not normalized here
    assert "mail" in first.entities              # predecoder.hostname
    assert "172.17.131.81" in first.entities     # agent.ip
    assert first.description.startswith("Jan 15 02:32:32 mail freshclam")
    # The original record is preserved verbatim for provenance / later use.
    assert first.raw["rule"]["id"] == "52507"


def test_missing_id_raises():
    with pytest.raises(ValueError):
        wazuh_record_to_raw_alert({"@timestamp": "2022-01-15T02:32:32Z", "rule": {}})


def test_missing_timestamp_raises():
    with pytest.raises(ValueError):
        wazuh_record_to_raw_alert({"id": "abc", "rule": {}})