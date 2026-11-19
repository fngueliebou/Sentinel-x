"""Run the initial baselines over the reference scenarios and write a run manifest.

Scenario source of truth is data/scenarios/*.json. Each file is a full Scenario
(inline alert + reference disposition + documented ground-truth provenance). This
replaces the earlier evals/scenarios/sample_scenarios.json pointer list, which
duplicated three of these cases as bare `alert_file` references (the raw alert
fixtures in data/alerts/ remain, used by unit tests). See CHANGELOG.

Records, per EVALUATION.md: knowledge version, LLM provider+model, prompt
version, decoding (temperature/seed), per-scenario disposition vs reference
ground truth, per-baseline agreement, and cost (0.0 for the offline stub). Writes
a JSON manifest to evals/results/.
"""

from __future__ import annotations

import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from sentinelx.config import load_settings
from sentinelx.investigation import PROMPT_VERSION, investigate
from sentinelx.normalization import normalize_alert
from sentinelx.knowledge import load_sample_store
from sentinelx.llm import get_provider
from sentinelx.schemas import Scenario
from sentinelx.triage import triage

from evals.baselines import BASELINES

_KNOWLEDGE_VERSION = "sample-2026-10-22"
_SCENARIO_DIR = Path("data/scenarios")
_RESULTS_DIR = Path("evals/results")


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return "unknown"


def _load_scenarios() -> list[tuple[str, Scenario]]:
    """Every Scenario in data/scenarios/, sorted by filename for stable output."""
    out: list[tuple[str, Scenario]] = []
    for path in sorted(_SCENARIO_DIR.glob("*.json")):
        sc = Scenario.model_validate(json.loads(path.read_text(encoding="utf-8")))
        out.append((path.name, sc))
    return out


def report_cost(report) -> float | None:
    # The offline stub reports cost 0.0; a real provider would carry usage/cost.
    return 0.0 if report.llm_provider == "deterministic" else None


def _run_baseline_on_alert(baseline_key: str, raw_alert, settings, store) -> dict:
    """Run one baseline on one (raw) alert and return its disposition row fields.

    A  -> deterministic triage, no LLM.
    B  -> provider (default stub), no retrieval.
    C  -> provider (default stub) + RAG over the sample store.
    """
    normalized = normalize_alert(raw_alert)

    if baseline_key == "A":
        d = triage(normalized)
        return {"disposition": d.disposition.value, "verification_passed": None, "cost_usd": 0.0}

    provider = get_provider(settings)
    use_rag = baseline_key == "C"
    report = investigate(
        normalized,
        provider=provider,
        store=store if use_rag else None,
        use_rag=use_rag,
        top_k=settings.retrieval_top_k,
    )
    return {
        "disposition": report.disposition.value,
        "verification_passed": report.verification_passed,
        "cost_usd": report_cost(report),
    }


def _initial_context_ground_truth(sc) -> tuple[str, str]:
    """Ground truth a TOOL-LESS baseline (A/B/C) is scored against, plus its basis.

    Tool-less baselines only ever see the initial alert context, so they are always
    scored on INITIAL-CONTEXT triage.
    """
    if sc.requires_tool_retrieval:
        if sc.initial_context_disposition is None:
            raise ValueError(
                f"{sc.scenario_id}: requires_tool_retrieval=True but "
                "initial_context_disposition is not set."
            )
        return sc.initial_context_disposition.value, "initial_context_disposition"
    return sc.expected_disposition.value, "expected_disposition"


def evaluate(settings, store, scenarios) -> dict:
    """Run every runnable baseline over every scenario; return per-baseline results.

    Baselines A/B/C are TOOL-LESS: each runs on `sc.alert` only. `retrievable_events`
    are never passed to them (that would defeat the tool-retrieval design), so these
    rows measure initial-context triage, scored via _initial_context_ground_truth.
    """
    runnable = [b for b in BASELINES.values() if b.implemented]
    per_baseline: dict[str, dict] = {}
    for b in runnable:
        rows = []
        agree = 0
        for fname, sc in scenarios:
            ground_truth, basis = _initial_context_ground_truth(sc)
            # sc.alert carries ONLY the initial context; retrievable_events are excluded.
            res = _run_baseline_on_alert(b.key, sc.alert, settings, store)
            match = res["disposition"] == ground_truth
            agree += int(match)
            row = {
                "scenario_file": fname,
                "scenario_id": sc.scenario_id,
                "capability_evaluated": "triage_initial_context_no_tools",
                "ground_truth": ground_truth,
                "ground_truth_basis": basis,
                "got": res["disposition"],
                "match": match,
                "verification_passed": res["verification_passed"],
                "cost_usd": res["cost_usd"],
            }
            if sc.requires_tool_retrieval:
                # Record (but do not score) the post-investigation reference, and spell out what a match means here so the row is not misread as detection.
                row["post_investigation_reference"] = sc.expected_disposition.value
                row["match_meaning"] = (
                    "match=true means the initial-context triage matches the chosen "
                    "initial_context_disposition reference; it does NOT mean the "
                    "compromise was detected (that requires tool retrieval / Baseline D, "
                    "not implemented)."
                )
            rows.append(row)
        per_baseline[b.key] = {
            "label": b.label,
            "agreement_with_ground_truth": f"{agree}/{len(scenarios)}",
            "rows": rows,
        }
    return per_baseline


def main() -> int:
    settings = load_settings()
    store = load_sample_store()
    scenarios = _load_scenarios()

    runnable = [b for b in BASELINES.values() if b.implemented]
    per_baseline = evaluate(settings, store, scenarios)

    manifest = {
        "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "python": platform.python_version(),
        "scenario_source": str(_SCENARIO_DIR / "*.json"),
        "scenario_count": len(scenarios),
        "scenario_ids": [sc.scenario_id for _, sc in scenarios],
        "capability_evaluated": (
            "Baselines A/B/C evaluate INITIAL-CONTEXT triage without tools. For "
            "requires_tool_retrieval scenarios the decisive evidence is in "
            "retrievable_events (never given to these baselines) and their "
            "post-investigation disposition is not evaluated here (needs Baseline D, "
            "not implemented). A match on such a scenario means correct initial-context "
            "triage against a chosen reference, not detection of the compromise."
        ),
        "tool_retrieval_scenarios": [
            sc.scenario_id for _, sc in scenarios if sc.requires_tool_retrieval
        ],
        "scoring_note": (
            "Tool-less baselines are scored per scenario via ground_truth_basis: "
            "'expected_disposition' for full-context scenarios (unchanged from before, "
            "so historical per-scenario results stay comparable) and "
            "'initial_context_disposition' for tool-retrieval scenarios. Adding a "
            "tool-retrieval scenario raises the denominator but does not alter how any "
            "existing scenario is scored."
        ),
        "knowledge_version": _KNOWLEDGE_VERSION,
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_model,
        "llm_temperature": settings.llm_temperature,
        "llm_seed": settings.llm_seed,
        "prompt_version": PROMPT_VERSION,
        "baselines_run": [b.key for b in runnable],
        "baselines_not_implemented": [k for k, b in BASELINES.items() if not b.implemented],
        "results": per_baseline,
        "disclaimer": (
            "Not a scientific benchmark. Hand-authored synthetic + AIT-ADS-grounded "
            "reference cases; ground truth = reference-analyst disposition informed by "
            "the dataset time_label, not a certified event_label. Tool-retrieval "
            "scenarios are scored only on initial-context triage (see "
            "capability_evaluated). The default analyst is a deterministic rule-based "
            "stub; no value here is real-LLM performance. See docs/EVALUATION.md."
        ),
    }

    _RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = _RESULTS_DIR / f"run_{manifest['run_id']}.json"
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    print(f"\nManifest written to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())