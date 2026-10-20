"""Tests for the labeled scan / descriptive summary (sentinelx.datasets.ait_ads).

Ties the loader and the labels together on the committed fixture. The fixture
alerts are ClamAV updates at 2022-01-15 02:32 UTC, well before any real fox
attack window, so with the real windows they are all benign; a hand-built window
covering that instant exercises the attack path on the same real records.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sentinelx.datasets.ait_ads import summarize_labeled_wazuh
from sentinelx.datasets.ait_ads_labels import AttackWindow

_SAMPLE = Path(__file__).resolve().parent / "data" / "ait_ads" / "fox_wazuh.sample.jsonl"


def _utc(epoch: float) -> datetime:
    return datetime.fromtimestamp(epoch, tz=timezone.utc)


def test_summary_all_benign_without_windows():
    summary = summarize_labeled_wazuh(_SAMPLE, [])
    assert summary.total == 3
    assert summary.benign == 3
    assert summary.attack_total == 0
    assert summary.per_attack == {}


def test_summary_counts_attacks_inside_a_window():
    # The three fixture records fall at 02:32:32 / 02:32:32 / 02:32:37 UTC on
    # 2022-01-15 (epoch 1642213952..1642213957). This window covers all three.
    window = AttackWindow(
        scenario="fox",
        attack="test_attack",
        start=_utc(1642213900),
        end=_utc(1642214000),
    )
    summary = summarize_labeled_wazuh(_SAMPLE, [window])
    assert summary.total == 3
    assert summary.benign == 0
    assert summary.per_attack == {"test_attack": 3}


def test_summary_limit_stops_early():
    summary = summarize_labeled_wazuh(_SAMPLE, [], limit=1)
    assert summary.total == 1


def test_summary_tracks_time_range():
    summary = summarize_labeled_wazuh(_SAMPLE, [])
    assert summary.first_timestamp == _utc(1642213952)  # 02:32:32 UTC
    assert summary.last_timestamp == _utc(1642213957)   # 02:32:37 UTC