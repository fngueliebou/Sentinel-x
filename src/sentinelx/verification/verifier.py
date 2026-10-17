"""Independent citation verification (grounding check).

This is a deterministic check, separate from the analysis step: it does not trust
the provider's own claim of groundedness. For every FACT, each citation must
resolve to an evidence id that actually exists in the report's evidence set. Any
FACT with a dangling or missing citation is marked unsupported and the report
fails verification.

This is a first, mechanical layer. The richer "independent challenge" of
investigation conclusions (N4) and the groundedness metrics (EVALUATION.md §7)
build on top of it and are NOT YET IMPLEMENTED.
"""

from __future__ import annotations

from sentinelx.schemas import FindingKind, InvestigationReport


def verify_report(report: InvestigationReport) -> InvestigationReport:
    valid_ids = report.evidence_ids()
    notes: list[str] = []
    all_ok = True

    def _check(findings, require_citation: bool) -> None:
        nonlocal all_ok
        for f in findings:
            dangling = [c.evidence_id for c in f.citations if c.evidence_id not in valid_ids]
            if dangling:
                f.supported = False
                all_ok = False
                notes.append(
                    f"{f.kind.value}: citations not found in evidence set: {dangling}"
                )
            elif require_citation and not f.citations:
                f.supported = False
                all_ok = False
                notes.append(f"{f.kind.value}: FACT without citation: {f.statement!r}")
            else:
                f.supported = True

    _check(report.facts, require_citation=True)
    # Non-fact findings may cite evidence; if they do, dangling ids are still errors.
    _check(report.hypotheses, require_citation=False)
    _check(report.unknowns, require_citation=False)
    _check(report.recommendations, require_citation=False)

    # Surface injection-flagged evidence as an informational note (no control-flow effect).
    flagged = [e.id for e in report.evidence if e.untrusted_flags]
    if flagged:
        notes.append(
            "Injection-like patterns flagged in evidence (informational, not acted upon): "
            + ", ".join(flagged)
        )

    report.verification_passed = all_ok
    report.verification_notes = notes
    return report
