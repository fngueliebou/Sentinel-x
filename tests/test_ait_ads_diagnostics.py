"""Tests for AIT-ADS rule-composition diagnostics.

The pure accumulator is tested on synthetic records (exhaustive, fast); one
integration test runs the file-based entry point on the committed fixture.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from sentinelx.datasets.ait_ads_diagnostics import (
    accumulate_rule_stats,
    diagnose_wazuh_rules,
)

_SAMPLE = Path(__file__).resolve().parent / "data" / "ait_ads" / "fox_wazuh.sample.jsonl"


def test_basic_counts_and_ambiguity():
    labeled = [
        ({"rule": {"id": "R1", "description": "web scan", "groups": ["web"]}}, "dirb"),
        ({"rule": {"id": "R1", "description": "web scan", "groups": ["web"]}}, None),
        ({"rule": {"id": "R2", "description": "priv esc", "groups": ["syscall"]}}, "privilege_escalation"),
        ({"rule": {"id": "R3", "description": "cron", "groups": ["cron"]}}, None),
    ]
    diag = accumulate_rule_stats(labeled)
    assert diag.total == 4
    assert diag.attack == 2
    assert diag.benign == 2
    assert diag.per_attack_totals == Counter({"dirb": 1, "privilege_escalation": 1})
    assert diag.rules["R1"].is_ambiguous      # fires attack AND benign
    assert not diag.rules["R2"].is_ambiguous
    assert diag.group_totals["web"] == 2


def test_attack_only_and_benign_only():
    labeled = [
        ({"rule": {"id": "R2", "description": "x", "groups": []}}, "a"),
        ({"rule": {"id": "R2", "description": "x", "groups": []}}, "a"),
        ({"rule": {"id": "R3", "description": "y", "groups": []}}, None),
    ]
    diag = accumulate_rule_stats(labeled)
    assert [r.rule_id for r in diag.attack_only_rules()] == ["R2"]
    assert [r.rule_id for r in diag.benign_only_rules()] == ["R3"]


def test_leakage_counts_attack_alerts_on_benign_capable_rules():
    labeled = [
        ({"rule": {"id": "R1"}}, "dirb"),   # R1 attack
        ({"rule": {"id": "R1"}}, None),     # R1 also benign -> benign-capable
        ({"rule": {"id": "R2"}}, "x"),      # R2 attack only
    ]
    diag = accumulate_rule_stats(labeled)
    # Only R1's single attack alert sits on a benign-capable rule.
    assert diag.attack_alerts_on_benign_capable_rules == 1


def test_missing_fields_and_embedded_label_detection():
    labeled = [
        ({"rule": {}}, None),                                 # missing id/desc/groups
        ({"rule": {"id": "R1"}, "event_label": "-"}, "a"),    # embedded label key present
    ]
    diag = accumulate_rule_stats(labeled)
    assert diag.missing_rule_id == 1
    assert diag.missing_description == 2
    assert diag.missing_groups == 2
    assert diag.embedded_label_present == 1
    assert "<missing>" in diag.rules


def test_diagnose_on_fixture_file_all_benign():
    diag = diagnose_wazuh_rules(_SAMPLE, [])  # no windows -> all benign
    assert diag.total == 3
    assert diag.benign == 3
    assert diag.attack == 0
    assert "52507" in diag.rules
    assert diag.rules["52507"].description == "ClamAV database update"
    assert diag.embedded_label_present == 0  # confirms records carry no label field