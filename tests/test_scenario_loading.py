"""Test that the shipped scenario file loads and validates against the Scenario contract.

This guards the on-disk ground-truth data: if a scenario file drifts out of shape
(e.g. a key_evidence_event_id that no longer matches an event), this test fails.
Run from the repository root (pytest is configured that way), so the relative path
resolves.
"""

from __future__ import annotations

import json
from pathlib import Path

from sentinelx.schemas import Disposition, Scenario

SCENARIO_PATH = Path("data/scenarios/scenario_bruteforce.json")


def test_bruteforce_scenario_loads_and_validates():
    # Read the raw JSON from disk, then let the Scenario contract validate it.
    payload = json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))
    scenario = Scenario.model_validate(payload)

    # Spot-check a few fields so the test documents what the scenario asserts.
    assert scenario.scenario_id == "SC-BRUTEFORCE-001"
    assert scenario.expected_disposition == Disposition.ESCALATE
    assert "T1110" in scenario.expected_techniques

    # Every key-evidence id must correspond to a real event in the alert. The
    # Scenario validator already enforces this at construction time; we assert the
    # linkage explicitly here as living documentation of the invariant.
    event_ids = {event.id for event in scenario.alert.events}
    assert set(scenario.key_evidence_event_ids).issubset(event_ids)