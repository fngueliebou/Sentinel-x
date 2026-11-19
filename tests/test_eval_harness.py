"""Harness-level checks for evals.run_eval over data/scenarios/*.json.

These assert the evaluation machinary and one cross-suite invariant, not a
specific score. Observed behavior (recorded, not predicted):

- Every runnable baseline (A/B/C) is evaluated on every scenario file.
- For the deterministic stub, RAG (C) never changes the disposition vs no-RAG
  (B) across the whole suite -> the stub's decision is retrieval-independent
"""

from __future__ import annotations

from sentinelx.config import Settings
from sentinelx.knowledge import load_sample_store

from evals.baselines import BASELINES
from evals.run_eval import _load_scenarios, evaluate

_DETERMINISTIC = Settings(llm_provider="deterministic")


def _results():
    scenarios = _load_scenarios()
    store = load_sample_store()
    return scenarios, evaluate(_DETERMINISTIC, store, scenarios)


def test_every_runnable_baseline_covers_every_scenario():
    scenarios, results = _results()
    runnable_keys = {k for k, b in BASELINES.items() if b.implemented}
    assert set(results) == runnable_keys  # exactly A/B/C today
    scenario_ids = {sc.scenario_id for _, sc in scenarios}
    for key, res in results.items():
        got_ids = {r["scenario_id"] for r in res["rows"]}
        assert got_ids == scenario_ids, f"baseline {key} did not cover all scenarios"
        # agreement string is well-formed "n/total"
        agree_str = res["agreement_with_ground_truth"]
        n, total = agree_str.split("/")
        assert int(total) == len(scenarios)
        assert 0 <= int(n) <= len(scenarios)


def test_reference_scenarios_are_included():
    scenarios, _ = _results()
    ids = {sc.scenario_id for _, sc in scenarios}
    # The two real AIT-grounded cases must be part of the evaluated suite.
    assert {"fox-privesc-shadow", "fox-dnsteal-dns-exfil"} <= ids


def test_rag_is_disposition_invariant_for_the_stub():
    _scenarios, results = _results()
    # C (LLM+RAG) and B (LLM no RAG) must yield identical dispositions per scenario
    # for the deterministic stub: its decision is derived from structured signals,
    # never from retrieved knowledge.
    b_by_id = {r["scenario_id"]: r["got"] for r in results["B"]["rows"]}
    c_by_id = {r["scenario_id"]: r["got"] for r in results["C"]["rows"]}
    assert b_by_id == c_by_id


def test_stub_runs_report_zero_cost():
    _scenarios, results = _results()
    # The offline stub carries no API cost; A reports 0.0, B/C report 0.0 (not None).
    for key in ("A", "B", "C"):
        for r in results[key]["rows"]:
            assert r["cost_usd"] == 0.0


# --- Capability-aware scoring (tool-retrieval scenarios) ------------------------

def test_all_rows_are_labelled_initial_context_triage():
    _scenarios, results = _results()
    # Every row must declare the capability it measures and the basis of its ground truth, so no comparison is implicit.
    for key in ("A", "B", "C"):
        for r in results[key]["rows"]:
            assert r["capability_evaluated"] == "triage_initial_context_no_tools"
            assert r["ground_truth_basis"] in {
                "expected_disposition",
                "initial_context_disposition",
            }


def test_full_context_scenarios_scored_against_expected_disposition():
    # No regression: scenarios without tool retrieval keep being scored against
    # expected_disposition exactly as before the capability-aware change.
    scenarios, results = _results()
    non_tool = {
        sc.scenario_id for _, sc in scenarios if not sc.requires_tool_retrieval
    }
    assert non_tool  # sanity
    for key in ("A", "B", "C"):
        for r in results[key]["rows"]:
            if r["scenario_id"] in non_tool:
                assert r["ground_truth_basis"] == "expected_disposition"


def test_tool_retrieval_scenario_scored_on_initial_context_not_detection():
    scenarios, results = _results()
    tool_ids = {sc.scenario_id for _, sc in scenarios if sc.requires_tool_retrieval}
    assert "fox-cracking-webmail-cred" in tool_ids  # the N3 case is present
    for key in ("A", "B", "C"):
        row = next(
            r for r in results[key]["rows"]
            if r["scenario_id"] == "fox-cracking-webmail-cred"
        )
        # Scored against the chosen initial-context reference, not post-investigation.
        assert row["ground_truth_basis"] == "initial_context_disposition"
        assert row["ground_truth"] == "insufficient_evidence"
        assert row["post_investigation_reference"] == "escalate"
        # The row must spell out that a match is NOT detection of the compromise.
        assert "does NOT mean the" in row["match_meaning"]


def test_retrievable_events_are_not_fed_to_tool_less_baselines():
    scenarios, _ = _results()
    sc = next(sc for _, sc in scenarios if sc.scenario_id == "fox-cracking-webmail-cred")

    def is_decisive_success(e):
        return (
            e.attributes.get("rule_id") == "9701"
            and e.attributes.get("user") == "christopher.friedman"
        )

    assert not any(is_decisive_success(e) for e in sc.alert.events)
    assert any(is_decisive_success(e) for e in sc.retrievable_events)