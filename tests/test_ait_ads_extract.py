"""Tests for attack-phase alert extraction (sentinelx.datasets.ait_ads)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sentinelx.datasets.ait_ads import iter_alerts_for_attacks
from sentinelx.datasets.ait_ads_labels import AttackWindow

_SAMPLE = Path(__file__).resolve().parent / "data" / "ait_ads" / "fox_wazuh.sample.jsonl"


def _utc(epoch: float) -> datetime:
    return datetime.fromtimestamp(epoch, tz=timezone.utc)


# Window covering the three fixture records (02:32:32..02:32:37 UTC on 2022-01-15).
_WINDOW = AttackWindow(
    scenario="fox", attack="privilege_escalation",
    start=_utc(1642213900), end=_utc(1642214000),
)


def test_no_windows_yields_nothing():
    assert list(iter_alerts_for_attacks(_SAMPLE, [])) == []


def test_all_attacks_yields_every_labeled_alert():
    results = list(iter_alerts_for_attacks(_SAMPLE, [_WINDOW]))
    assert len(results) == 3
    assert all(attack == "privilege_escalation" for _, attack in results)


def test_filter_keeps_only_requested_attack():
    kept = list(iter_alerts_for_attacks(_SAMPLE, [_WINDOW], attacks={"privilege_escalation"}))
    assert len(kept) == 3
    missed = list(iter_alerts_for_attacks(_SAMPLE, [_WINDOW], attacks={"dnsteal"}))
    assert missed == []