"""Tests that every shipped scenario file loads and validates against the Scenario contract.

Uses pytest parametrization: the test function runs once PER scenario file found in
data/scenarios/, so adding a new scenario file automatically adds a test case — no
test code to change. Run from the repository root (pytest is configured that way),
so the relative path resolves.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sentinelx.schemas import Scenario

SCENARIO_DIR = Path("data/scenarios")
# Collected at import time (collection), relative to the repo root where pytest runs.
SCENARIO_FILES = sorted(SCENARIO_DIR.glob("*.json"))


def test_scenario_directory_is_not_empty():
    # Guard: if the glob found nothing, every parametrized test would silently be
    # skipped. This makes "no scenarios" an explicit failure instead.
    assert SCENARIO_FILES, "no scenario files found in data/scenarios/"


@pytest.mark.parametrize("scenario_file", SCENARIO_FILES, ids=lambda p: p.stem)
def test_scenario_file_loads_and_validates(scenario_file: Path):
    payload = json.loads(scenario_file.read_text(encoding="utf-8"))
    scenario = Scenario.model_validate(payload)

    # Invariant: every key-evidence id must reference a real event, in the initial
    # alert OR the retrievable set. The Scenario validator enforces this at
    # construction; we assert it explicitly as living documentation of the contract.
    event_ids = {event.id for event in scenario.alert.events}
    retrievable_ids = {event.id for event in scenario.retrievable_events}
    assert set(scenario.key_evidence_event_ids).issubset(event_ids | retrievable_ids)
    # And the two sets must not share an id (single home per event).
    assert event_ids.isdisjoint(retrievable_ids)

    # Each scenario must carry a non-empty reference conclusion (the gold answer).
    assert scenario.reference_conclusion.strip()