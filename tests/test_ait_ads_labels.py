"""Tests for AIT-ADS ground-truth labels (sentinelx.datasets.ait_ads_labels).

Uses a tiny committed labels fixture (real fox + russellmitchell rows). The
boundary test pins the half-open [start, end) semantics that keep any instant
from being labeled with two attacks.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from sentinelx.datasets.ait_ads_labels import attack_at, load_attack_windows

_LABELS = Path(__file__).resolve().parent / "data" / "ait_ads" / "labels.sample.csv"


def _utc(epoch: float) -> datetime:
    return datetime.fromtimestamp(epoch, tz=timezone.utc)


def test_load_filters_by_scenario_and_orders():
    fox = load_attack_windows(_LABELS, "fox")
    assert [w.attack for w in fox] == ["network_scans", "service_scans", "wpscan", "dirb"]
    rm = load_attack_windows(_LABELS, "russellmitchell")
    assert len(rm) == 2
    assert all(w.scenario == "russellmitchell" for w in rm)


def test_attack_at_inside_window():
    fox = load_attack_windows(_LABELS, "fox")
    assert attack_at(fox, _utc(1642507200)) == "network_scans"


def test_attack_at_boundary_is_half_open():
    fox = load_attack_windows(_LABELS, "fox")
    # 1642508220 is network_scans.end AND service_scans.start -> belongs to service_scans.
    assert attack_at(fox, _utc(1642508220)) == "service_scans"


def test_attack_at_before_all_windows_is_benign():
    fox = load_attack_windows(_LABELS, "fox")
    assert attack_at(fox, _utc(1642500000)) is None


def test_attack_at_final_end_is_exclusive():
    fox = load_attack_windows(_LABELS, "fox")
    assert attack_at(fox, _utc(1642509480)) is None  # final window end is exclusive


def test_bad_header_raises(tmp_path: Path):
    bad = tmp_path / "bad.csv"
    bad.write_text("a,b,c\n1,2,3\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_attack_windows(bad, "fox")