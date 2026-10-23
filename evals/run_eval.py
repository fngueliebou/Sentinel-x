"""Run the initial baselines over the reference scenarios and write a run manifest.

Scenario source of truth is data/scenarios/*.json. Each file is a full Scenario
(inline alert + reference disposition + documented ground-truth provenance). This
replaces the earlier evals/scenarios/sample_scenarios.json pointer list, which
duplicated three of these cases as bare `alert_file` references (the raw alert
fixtures in data/alerts/ remain, used by unit tests). See CHANGELOG.

Records, per EVALUATION.md §10: knowledge version, LLM provider+model, prompt
version, decoding (temperature/seed), per-scenario disposition vs reference
ground truth, per-baseline agreement, and cost (0.0 for the offline stub). Writes
a JSON manifest to evals/results/.

This is NOT a scientific benchmark. The suite is five scenarios: three
hand-authored synthetic cases and two AIT-ADS-grounded reference cases whose
"ground truth" is a reference-analyst disposition informed by the dataset
time_label (NOT a certified per-event label). The default analyst is a
deterministic rule-based stub, so no number here is real-LLM performance.

    python -m evals.run_eval
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


def evaluate(settings, store, scenarios) -> dict:
    """Run every runnable baseline over every scenario; return per-baseline results."""
    runnable = [b for b in BASELINES.values() if b.implemented]
    per_baseline: dict[str, dict] = {}
    for b in runnable:
        rows = []
        agree = 0
        for fname, sc in scenarios:
            expected = sc.expected_disposition.value
            res = _run_baseline_on_alert(b.key, sc.alert, settings, store)
            match = res["disposition"] == expected
            agree += int(match)
            rows.append(
                {
                    "scenario_file": fname,
                    "scenario_id": sc.scenario_id,
                    "ground_truth": expected,
                    "got": res["disposition"],
                    "match": match,
                    "verification_passed": res["verification_passed"],
                    "cost_usd": res["cost_usd"],
                }
            )
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
            "NOT a scientific benchmark. Five scenarios (three hand-authored "
            "synthetic + two AIT-ADS-grounded reference cases, ground truth = "
            "reference-analyst disposition informed by the dataset time_label, "
            "not a certified event_label). The default analyst is a deterministic "
            "rule-based stub; no value here is real-LLM performance. "
            "See docs/EVALUATION.md."
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