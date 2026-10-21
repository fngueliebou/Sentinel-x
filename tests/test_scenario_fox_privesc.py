"""Loading + integrity test for the fox-privesc-shadow reference scenario.

This scenario is grounded in 10 REAL AIT-ADS fox Wazuh alerts (extracted via
scripts/extract_ait_ads_attack.py). The test checks it validates against the
Scenario contract and that its ids, provenance and ground-truth fields are
coherent. It does NOT assert anything about detection performance.
"""

from __future__ import annotations

import json
from pathlib import Path

from sentinelx.schemas import Scenario
from sentinelx.schemas.enums import Disposition

_SCENARIO = Path("data/scenarios/scenario_fox_privesc_shadow.json")


def _load() -> Scenario:
    return Scenario.model_validate(json.loads(_SCENARIO.read_text(encoding="utf-8")))


def test_scenario_loads_and_core_fields():
    sc = _load()
    assert sc.scenario_id == "fox-privesc-shadow"
    # 'escalate' is a triage DECISION from the real enum (not a 'true_positive' class).
    assert sc.expected_disposition is Disposition.ESCALATE
    assert sc.reference_conclusion.strip()


def test_ten_real_events_with_unique_ids():
    sc = _load()
    ids = [e.id for e in sc.alert.events]
    assert len(ids) == 10
    assert len(set(ids)) == 10  # unique within our representation


def test_event_provenance_is_preserved():
    sc = _load()
    # Every event keeps its original Wazuh id and these are all distinct (real alerts).
    originals = [e.attributes.get("original_wazuh_id") for e in sc.alert.events]
    assert all(originals)
    assert len(set(originals)) == 10
    # The trigger alert is the su event (e1) and shares its real Wazuh id.
    assert sc.alert.id == "1686444911.263244326"


def test_key_evidence_subset_and_shadow_present():
    sc = _load()
    event_ids = {e.id for e in sc.alert.events}
    assert set(sc.key_evidence_event_ids).issubset(event_ids)
    # The decisive /etc/shadow command is among the events and in key evidence.
    shadow = [e for e in sc.alert.events if "/etc/shadow" in e.message]
    assert len(shadow) == 1
    assert shadow[0].id in sc.key_evidence_event_ids


def test_attack_techniques_are_only_the_observed_ones():
    sc = _load()
    # Observed-execution techniques only; T1078 / T1505.003 are NOT asserted here.
    assert sc.expected_techniques == ["T1548.003", "T1003.008"]


def test_label_provenance_documented_as_time_label():
    sc = _load()
    assert "time_label" in sc.metadata.get("label_provenance", "")
    # Legitimate unknowns are carried in ground truth, not invented away.
    assert sc.expected_unknowns