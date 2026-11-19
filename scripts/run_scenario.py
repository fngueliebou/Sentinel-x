"""Run one investigation Scenario through the deterministic pipeline.

Baseline B (default)   : deterministic provider, No retrieval.
Baseline C (--rag)     : deterministic provider + RAG over the sample knowledge store.

Loads a Scenario (which also carries its ground truth), runs the existing pipeline
on scenario.alert, prints the structured report, then a descriptive comparison
against the scenario's expectations.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sentinelx.pipeline import run_investigation
from sentinelx.schemas import InvestigationReport, Scenario, SourceType


def load_scenario(path: str | Path) -> Scenario:
    """Load and validate a Scenario JSON (ground truth included)"""
    return Scenario.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))


def run_pipeline(scenario: Scenario, *, use_rag: bool) -> InvestigationReport:
    """Run the existing pipeline with the deterministic provider"""
    return run_investigation(scenario.alert, use_rag=use_rag)


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
    """Return the Evidence built from a given scenario event id"""
    target = f"event:{event_id}"
    for e in report.evidence:
        if e.source_ref == target:
            return e
    return None


def print_report_and_comparison(
    scenario: Scenario, report: InvestigationReport, *, baseline: str
) -> None:
    rag_label = "deterministic + RAG" if baseline == "C" else "deterministic, no RAG"
    print("=" * 72)
    print(f"SCENARIO {scenario.scenario_id}  (Baseline {baseline}: {rag_label})")
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
        score = f"  score={e.score}" if e.score is not None else ""
        print(f"    {e.id}  [{e.source_type.value}]  ref={e.source_ref}{score}{flags}")
        if e.source_type is SourceType.KNOWLEDGE:
            print(f"        content: {e.content[:180]}")

    # The report keeps claim types separate: facts / hypotheses / unknowns / recommendations.
    _print_findings("FACTS", report.facts)
    _print_findings("HYPOTHESES", report.hypotheses)
    _print_findings("UNKNOWNS", report.unknowns)
    _print_findings("RECOMMENDATIONS", report.recommendations)

    # ---------- Descriptive comparison vs scenario ground truth (Not a score) ----------
    print("\n" + "-" * 72)
    print("Descriptive comparaison vs scenario expectations (observed gaps, not scoring):")

    same = report.disposition == scenario.expected_disposition
    print(
        f"\n  disposition: got '{report.disposition.value}'  |  "
        f"scenario reference '{scenario.expected_disposition.value}'  |  "
        f"{'MATCH' if same else 'DIFFERENT'}"
    )
    print("    (The scenario's expected_disposition is the reference triage decision a correct")
    print("     investigation should reach - not the AIT-ADS attack-phase label 'privilege_escalation'.)")

    print("\n  key evidence grounded as supported facts:")
    supported_fact_citations = {
        c.evidence_id for f in report.facts if f.supported for c in f.citations
    }
    for eid in scenario.key_evidence_event_ids:
        ev = _evidence_for_event(report, eid)
        if ev is None:
            print(f"    - {eid}: not present in the evidence set")
        elif ev.id in supported_fact_citations:
            print(f"    - {eid} -> {ev.id}: grounded in a supported fact")
        else:
            print(f"    - {eid} -> {ev.id}: present, but not cited by any supported fact")

    # ATT&CK coverage: do the expected techniques appear in the retrieved knowledge
    # This reports documentary coverage for this case only - never an RAG efficacy claim.
    kb = [e for e in report.evidence if e.source_type is SourceType.KNOWLEDGE]
    print(f"\n  expected ATT&CK techniques (scenario): {scenario.expected_techniques}")
    if not kb:
        print("    no knowledge retrieved (Baseline B / RAG disabled).")
    else:
        for tech in scenario.expected_techniques:
            haystack = " ".join(f"{e.source_ref} {e.content}" for e in kb).lower()
            found = tech.lower() in haystack
            print(f"    {tech}: {'present in retrieved knowledge' if found else 'not present in retrieved knowledge (coverage gap for this case)'}")
    print("    (The deterministic provider produces no ATT&CK mapping of its own.)")

    print(f"\n  scenario legitimate unknowns: {len(scenario.expected_unknowns)}  |  "
          f"report unknowns: {len(report.unknowns)}")
    print("    NOTE: if the report emits none of these unknowns, that reflects the STUB's behavior,")
    print("    not their absence from the data. The data supports these unknowns; the stub does not emit them.")
    print("-" * 72)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a Scenario through the deterministic pipeline (Baseline B, or C with --rag)."
    )
    parser.add_argument("scenario", type=Path, help="Path to a Scenario JSON file.")
    parser.add_argument(
        "--rag", action="store_true",
        help="Enable RAG over the sample knowledge store (Baseline C). Default off (Baseline B).",
    )
    args = parser.parse_args(argv)

    scenario = load_scenario(args.scenario)
    report = run_pipeline(scenario, use_rag=args.rag)
    print_report_and_comparison(scenario, report, baseline="C" if args.rag else "B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())