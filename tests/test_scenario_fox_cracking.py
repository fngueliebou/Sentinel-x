"""Artifact invariants for fox-cracking-webmail-cred (N3 tool-retrieval scenario).

Scope: this validates the scenario AS AN ARTIFACT (schema, honest structure, the
verified failure->success correspondence) and the ONE thing exercisable today —
that triage on the INITIAL context alone returns insufficient_evidence.

It deliberately does NOT assert that the compromise is detected: the decisive
success events are in retrievable_events, which no current baseline consumes
(requires_tool_retrieval=True). Tool execution / Baseline D is DEFERRED; nothing
here claims it works.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from sentinelx.config import Settings
from sentinelx.pipeline import run_investigation
from sentinelx.schemas import Disposition, Scenario

_SCENARIO = Path("data/scenarios/scenario_fox_cracking_webmail_cred.json")
_DETERMINISTIC = Settings(llm_provider="deterministic")


def _scenario() -> Scenario:
    return Scenario.model_validate(json.loads(_SCENARIO.read_text(encoding="utf-8")))


# --- Artifact shape --------------------------------------------------------------

def test_scenario_loads_and_is_marked_tool_retrieval():
    sc = _scenario()
    assert sc.scenario_id == "fox-cracking-webmail-cred"
    assert sc.requires_tool_retrieval is True
    assert sc.initial_context_disposition is Disposition.INSUFFICIENT_EVIDENCE
    assert sc.expected_disposition is Disposition.ESCALATE


def _is_decisive_success(e) -> bool:
    # The DECISIVE success = christopher.friedman's Dovecot auth-success. A benign
    # 9701 for another user is legitimate initial-context noise and does not count.
    return (
        e.attributes.get("rule_id") == "9701"
        and e.attributes.get("user") == "christopher.friedman"
    )


def test_initial_context_excludes_the_decisive_success():
    sc = _scenario()
    # The decisive success must NOT be in the initial context (a benign 9701 for
    # another user may be, as noise)...
    assert not any(_is_decisive_success(e) for e in sc.alert.events)
    # ...it is retrievable-only.
    assert any(_is_decisive_success(e) for e in sc.retrievable_events)


def test_key_evidence_spans_initial_and_retrievable():
    sc = _scenario()
    initial_ids = {e.id for e in sc.alert.events}
    retr_ids = {e.id for e in sc.retrievable_events}
    assert initial_ids.isdisjoint(retr_ids)  # no shared home (validator guarantee)
    key = set(sc.key_evidence_event_ids)
    assert key & initial_ids   # at least the trigger
    assert key & retr_ids      # at least one retrievable (the success)


def test_no_fabricated_attack_mapping():
    sc = _scenario()
    assert sc.expected_techniques == []
    cands = sc.metadata["attack_candidates"]
    assert "HYPOTHES" in cands.upper()
    assert "T1110" in cands and "T1078" in cands


def test_verified_failure_then_success_correspondence():
    sc = _scenario()
    all_events = list(sc.alert.events) + list(sc.retrievable_events)
    chris = [e for e in all_events if e.attributes.get("user") == "christopher.friedman"]
    # Every christopher.friedman event that carries a source IP shares the one
    # attacker source. (The Horde webmail failure has no source IP in its log, so it
    # is excluded here rather than asserted falsely.)
    chris_src_ips = {e.attributes.get("src_ip") for e in chris if e.attributes.get("src_ip")}
    assert chris_src_ips == {"192.168.128.195"}
    failures = [e for e in chris if e.attributes.get("rule_id") in {"5503", "9705", "2501"}]
    successes = [e for e in chris if e.attributes.get("rule_id") == "9701"]
    assert failures and successes
    # Verified ordering: every failure strictly precedes every success.
    last_fail = max(e.timestamp for e in failures)
    first_success = min(e.timestamp for e in successes)
    assert last_fail < first_success


def test_tls_distractors_are_on_other_hosts():
    sc = _scenario()
    # The honesty point: high-severity TLS alerts target hosts other than the
    # cracking target (taylorcruz-mail / 192.168.128.170).
    tls = [e for e in sc.alert.events if e.attributes.get("signature", "").startswith("SURICATA TLS")]
    assert tls
    tls_hosts = {e.attributes.get("dest_ip") for e in tls}
    assert "192.168.128.170" not in tls_hosts


# --- The one thing exercisable today: initial-context triage ---------------------

def test_initial_context_triage_is_insufficient_not_detection():
    sc = _scenario()
    # Run the tool-less pipeline on the INITIAL context only (sc.alert). This is NOT
    # an investigation: retrievable_events are not consumed. Observed behavior: the
    # stub returns insufficient_evidence, matching the chosen initial-context
    # reference. This is correct triage under limited input, NOT detection of the
    # credential compromise (which would require tool retrieval, not implemented).
    report = run_investigation(sc.alert, use_rag=False, settings=_DETERMINISTIC)
    assert report.disposition is Disposition.INSUFFICIENT_EVIDENCE
    assert report.disposition is sc.initial_context_disposition
    assert report.disposition is not sc.expected_disposition