"""Run the initial baselines over the sample scenarios and write a run manifest.

Records, per EVALUATION.md §10: dataset/sample version, LLM provider+model,
prompt version, decoding (temperature/seed), per-scenario dispositions vs ground
truth, aggregate agreement, and cost (0.0 for the offline stub). Writes a JSON
manifest to evals/results/.

This is a SAMPLE harness: agreement on 3 hand-authored scenarios is a smoke test,
not a scientific result. No metric here should be reported as model performance.

    python -m evals.run_eval
"""

from __future__ import annotations

import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from sentinelx.config import load_settings
from sentinelx.investigation import PROMPT_VERSION
from sentinelx.normalization import normalize_alert
from sentinelx.ingestion import load_raw_alert
from sentinelx.knowledge import load_sample_store
from sentinelx.llm import get_provider
from sentinelx.investigation import investigate
from sentinelx.triage import triage

from evals.baselines import BASELINES

_KNOWLEDGE_VERSION = "sample-2026-10-17"
_SCENARIOS = Path("evals/scenarios/sample_scenarios.json")
_RESULTS_DIR = Path("evals/results")


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return "unknown"


def _disposition_for(baseline_key: str, alert_file: str, settings, store) -> dict:
    raw = load_raw_alert(alert_file)
    normalized = normalize_alert(raw)

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
    cost = report_cost(report)
    return {
        "disposition": report.disposition.value,
        "verification_passed": report.verification_passed,
        "cost_usd": cost,
    }


def report_cost(report) -> float | None:
    # The offline stub reports cost 0.0; a real provider would carry usage/cost.
    return 0.0 if report.llm_provider == "deterministic" else None


def main() -> int:
    settings = load_settings()
    store = load_sample_store()
    scenarios = json.loads(_SCENARIOS.read_text(encoding="utf-8"))["scenarios"]

    runnable = [b for b in BASELINES.values() if b.implemented]

    per_baseline = {}
    for b in runnable:
        rows = []
        agree = 0
        for sc in scenarios:
            res = _disposition_for(b.key, sc["alert_file"], settings, store)
            match = res["disposition"] == sc["expected_disposition"]
            agree += int(match)
            rows.append(
                {
                    "alert_file": sc["alert_file"],
                    "expected": sc["expected_disposition"],
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

    manifest = {
        "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "python": platform.python_version(),
        "sample_scenarios_count": len(scenarios),
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
            "Sample smoke test on 3 hand-authored scenarios. NOT a scientific "
            "benchmark and NOT model performance. See docs/EVALUATION.md."
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
