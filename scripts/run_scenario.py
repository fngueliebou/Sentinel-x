#!/usr/bin/env python
"""Run one investigation Scenario through the deterministic pipeline (Baseline B).

Loads a Scenario (which also carries its ground truth), runs the EXISTING pipeline
on scenario.alert with the deterministic provider and NO RAG, prints the structured
report, then a DESCRIPTIVE comparison against the scenario's expectations.

This is a technical validation of the pipeline and an observation of the
deterministic provider's limits. It is NOT a performance measurement, NOT an LLM
evaluation, and does NOT validate the AIT-ADS time_label as certain ground truth.
It reuses only public functions; it changes nothing in src/, evals/ or the schemas.

Usage:
    python scripts/run_scenario.py data/scenarios/scenario_fox_privesc_shadow.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sentinelx.pipeline import run_investigation
from sentinelx.schemas import InvestigationReport, Scenario


def load_scenario(path: str | Path) -> Scenario:
    """Load and validate a Scenario JSON (ground truth included)."""
    return Scenario.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))


def run_baseline_b(scenario: Scenario) -> InvestigationReport:
    """Baseline B: deterministic provider, NO retrieval. No API, no network."""
    return run_investigation(scenario.alert, use_rag=False)


def _supported_label(value: bool | None) -> str:
    return {True: "supported", False: "UNSUPPORTED", None: "unverified"}[value]


def _print_findings(title: str, findings) -> None:
    print(f"\n  {title} ({len(findings)}):")
    if not findings:
        print("    (none)")
    for f in findings:
        cites = ", ".join(c.evidence_id for c in f.citations) or "—"
        print(f"    - [{_supported_label(f.supported)}] {f.statement}")
        print(f"        citations: {cites}")


def _evidence_for_event(report: InvestigationReport, event_id: str):
    """Return the Evidence built from a given scenario event id (source_ref=event:<id>)."""
    target = f"event:{event_id}"
    for e in report.evidence:
        if e.source_ref == target:
            return e
    return None


def print_report_and_comparison(scenario: Scenario, report: InvestigationReport) -> None:
    print("=" * 72)
    print(f"SCENARIO {scenario.scenario_id}  (Baseline B: deterministic provider, no RAG)")
    print("  Technical pipeline validation only - not a performance measurement,")
    print("  not an LLM evaluation; the AIT-ADS label is a time_label (not certain truth).")
    print("=" * 72)

    print(f"\nPROVIDER: {report.llm_provider} / {report.llm_model}   prompt={report.prompt_version}")
    print(f"DISPOSITION (triage decision): {report.disposition.value}")
    print(f"SUMMARY: {report.summary}")
    print(f"VERIFICATION passed: {report.verification_passed}")
    for note in report.verification_notes:
        print(f"    note: {note}")

    print(f"\nEVIDENCE SET ({len(report.evidence)} items):")
    for e in report.evidence:
        flags = f"  flags={e.untrusted_flags}" if e.untrusted_flags else ""
        print(f"    {e.id}  [{e.source_type.value}]  ref={e.source_ref}{flags}")

    # The report keeps claim types separate: facts / hypotheses / unknowns / recommendations.
    _print_findings("FACTS", report.facts)
    _print_findings("HYPOTHESES", report.hypotheses)
    _print_findings("UNKNOWNS", report.unknowns)
    _print_findings("RECOMMENDATIONS", report.recommendations)

    # ---------- Descriptive comparison vs scenario ground truth (NOT a score) ----------
    print("\n" + "-" * 72)
    print("DESCRIPTIVE COMPARISON vs scenario expectations (observed gaps, not scoring):")

    same = report.disposition == scenario.expected_disposition
    print(
        f"\n  disposition: got '{report.disposition.value}'  |  "
        f"scenario reference '{scenario.expected_disposition.value}'  |  "
        f"{'MATCH' if same else 'DIFFERENT'}"
    )
    print("    (The scenario's expected_disposition is the reference TRIAGE DECISION a correct")
    print("     investigation should reach - NOT the AIT-ADS attack-phase label 'privilege_escalation'.)")

    print("\n  key evidence grounded as supported facts:")
    supported_fact_citations = {
        c.evidence_id for f in report.facts if f.supported for c in f.citations
    }
    for eid in scenario.key_evidence_event_ids:
        ev = _evidence_for_event(report, eid)
        if ev is None:
            print(f"    - {eid}: NOT present in the evidence set")
        elif ev.id in supported_fact_citations:
            print(f"    - {eid} -> {ev.id}: grounded in a supported fact")
        else:
            print(f"    - {eid} -> {ev.id}: present, but not cited by any supported fact")

    print(f"\n  expected ATT&CK techniques (scenario): {scenario.expected_techniques}")
    print("    The deterministic provider produces NO ATT&CK mapping (by design).")

    print(f"\n  scenario legitimate unknowns: {len(scenario.expected_unknowns)}  |  "
          f"report unknowns: {len(report.unknowns)}")
    print("    NOTE: if the report emits none of these unknowns, that reflects the STUB's behavior,")
    print("    not their absence from the data. The data supports these unknowns; the stub does not emit them.")
    print("-" * 72)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a Scenario through the deterministic pipeline (Baseline B, no RAG)."
    )
    parser.add_argument("scenario", type=Path, help="Path to a Scenario JSON file.")
    args = parser.parse_args(argv)

    scenario = load_scenario(args.scenario)
    report = run_baseline_b(scenario)
    print_report_and_comparison(scenario, report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())