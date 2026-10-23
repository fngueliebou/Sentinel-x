"""Harness-level checks for evals.run_eval over data/scenarios/*.json.

These assert the EVALUATION MACHINERY and one cross-suite invariant, not a
specific score. Observed behavior (recorded, not predicted):

- Every runnable baseline (A/B/C) is evaluated on every scenario file.
- For the deterministic stub, RAG (C) never changes the disposition vs no-RAG
  (B) across the whole suite -> the stub's decision is retrieval-independent.

The fact that the stub MISSES the two fox reference cases is an honest negative
result; it is asserted at the scenario level (test_run_scenario_fox_privesc.py,
test_scenario_fox_dnsteal.py), NOT frozen here, so that a future improvement to
the analyst is not reported as a regression by this file.

The deterministic provider is pinned via Settings so the run never depends on the
ambient environment / a local .env.
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