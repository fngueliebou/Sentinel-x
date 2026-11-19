"""Tests for the Scenario ground-truth contract (schemas/scenario.py)"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from sentinelx.schemas.alert import RawAlert
from sentinelx.schemas.scenario import Scenario


def _alert_with_events(event_ids: list[str]) -> RawAlert:
    """Build a minimal valid RawAlert carrying events with the given ids.

    Helper so each test can control exactly which event ids exist in the alert,
    which is what the cross-field validator checks against.
    """
    events = [
        {
            "id": eid,
            "timestamp": "2026-10-17T08:00:00Z",
            "source": "auth",
            "action": "login_failed",
            "message": "Failed password",
        }
        for eid in event_ids
    ]
    return RawAlert.model_validate(
        {
            "id": "ALERT-TEST",
            "source": "wazuh",
            "timestamp": "2026-10-17T08:00:00Z",
            "title": "test alert",
            "events": events,
        }
    )


def _minimal_scenario_kwargs() -> dict:
    """The five required fields, with an alert that has events e1 and e2."""
    return {
        "scenario_id": "SC-TEST-001",
        "description": "A test scenario.",
        "alert": _alert_with_events(["e1", "e2"]),
        "expected_disposition": "escalate",
        "reference_conclusion": "Reference conclusion text.",
    }


def test_valid_scenario_builds():
    # A scenario naming only events that exist (e1, e2) must build successfully.
    scenario = Scenario(
        **_minimal_scenario_kwargs(),
        expected_techniques=["T1110"],
        key_evidence_event_ids=["e1", "e2"],
        tags=["brute-force"],
    )
    assert scenario.scenario_id == "SC-TEST-001"
    assert scenario.key_evidence_event_ids == ["e1", "e2"]
    # Optional fields we did not pass default to empty containers.
    assert scenario.acceptable_conclusions == []
    assert scenario.metadata == {}


def test_empty_scenario_id_is_rejected():
    kwargs = _minimal_scenario_kwargs()
    kwargs["scenario_id"] = ""  # violates min_length=1
    with pytest.raises(ValidationError):
        Scenario(**kwargs)


def test_unknown_field_is_rejected():
    kwargs = _minimal_scenario_kwargs()
    kwargs["unexpected_field"] = 123  # violates extra="forbid"
    with pytest.raises(ValidationError):
        Scenario(**kwargs)


def test_missing_required_field_is_rejected():
    kwargs = _minimal_scenario_kwargs()
    del kwargs["reference_conclusion"]  # required field removed
    with pytest.raises(ValidationError):
        Scenario(**kwargs)


def test_dangling_key_evidence_is_rejected():
    kwargs = _minimal_scenario_kwargs()  # alert has events e1, e2
    kwargs["key_evidence_event_ids"] = ["e1", "e99"]  # e99 does not exist
    with pytest.raises(ValidationError) as exc_info:
        Scenario(**kwargs)
    # The error message should name the offending id, to help fix the scenario.
    assert "e99" in str(exc_info.value)


def test_default_lists_are_independent_between_instances():
    # Proves default_factory gives each instance its own list
    s1 = Scenario(**_minimal_scenario_kwargs())
    s2 = Scenario(**_minimal_scenario_kwargs())
    s1.tags.append("mutated")
    assert s2.tags == []  # s2 is unaffected -> lists are not shared