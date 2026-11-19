"""Offline, rule-based stand-in for an LLM analyst"""

from __future__ import annotations

from sentinelx.llm.base import AnalysisRequest, ProviderOutput, ProviderUsage
from sentinelx.schemas import (
    Citation,
    Disposition,
    Evidence,
    Finding,
    FindingKind,
    SourceType,
)
from sentinelx.constants import BRUTE_FORCE_FAILED_AUTH_THRESHOLD


def _is_failed_auth(ev: Evidence) -> bool:
    c = ev.content.lower()
    return "fail" in c or "authentication failure" in c


class DeterministicProvider:
    name = "deterministic"

    def analyze(self, request: AnalysisRequest) -> ProviderOutput:
        event_ev = [e for e in request.evidence if e.source_type == SourceType.EVENT]
        kb_ev = [e for e in request.evidence if e.source_type == SourceType.KNOWLEDGE]

        facts: list[Finding] = []
        failed_auth_ids: list[str] = []
        for ev in event_ev:
            # One grounded fact per event, citing exactly that event.
            facts.append(
                Finding(
                    kind=FindingKind.FACT,
                    statement=f"Telemetry event recorded: {ev.content}",
                    citations=[Citation(evidence_id=ev.id)],
                )
            )
            if _is_failed_auth(ev):
                failed_auth_ids.append(ev.id)

        # A grounded aggregate fact (only if there are failed-auth events to cite).
        if failed_auth_ids:
            facts.append(
                Finding(
                    kind=FindingKind.FACT,
                    statement=(
                        f"{len(failed_auth_ids)} failed-authentication event(s) observed."
                    ),
                    citations=[Citation(evidence_id=i) for i in failed_auth_ids],
                )
            )

        # Hypotheses come from retrieved knowledge (empty when RAG is disabled).
        hypotheses: list[Finding] = []
        recommendations: list[Finding] = []
        scanner_check_added = False
        for ev in kb_ev:
            hypotheses.append(
                Finding(
                    kind=FindingKind.HYPOTHESIS,
                    statement=(
                        "Observed activity may relate to: "
                        f"{ev.source_ref}. See retrieved knowledge."
                    ),
                    citations=[Citation(evidence_id=ev.id)],
                )
            )
            # Recommend the approved-scanner check once, and only for knowledge that
            # is actually about scanners (match "scanner", not merely "benign" in an
            # unrelated sentence). This removes a duplicate/false-positive reco.
            if not scanner_check_added and "scanner" in ev.content.lower():
                recommendations.append(
                    Finding(
                        kind=FindingKind.RECOMMENDATION,
                        statement=(
                            "Check the source address against the approved-scanner "
                            "inventory (read-only) before escalating."
                        ),
                        citations=[Citation(evidence_id=ev.id)],
                    )
                )
                scanner_check_added = True

        # Unknowns: acknowledged gaps (missing fields + no-telemetry case).
        unknowns: list[Finding] = [
            Finding(kind=FindingKind.UNKNOWN, statement=f"Missing field in alert: {m}")
            for m in request.alert.missing_fields
        ]
        if not event_ev:
            unknowns.append(
                Finding(
                    kind=FindingKind.UNKNOWN,
                    statement="No telemetry events available to substantiate the alert.",
                )
            )

        # Default read-only recommendation.
        if event_ev:
            recommendations.append(
                Finding(
                    kind=FindingKind.RECOMMENDATION,
                    statement="Review the cited authentication events for the affected entity.",
                    citations=[Citation(evidence_id=event_ev[0].id)],
                )
            )

        # Disposition from structured signal only.
        if not event_ev:
            disposition = Disposition.INSUFFICIENT_EVIDENCE
            summary = "No telemetry available; cannot substantiate a disposition."
        elif len(failed_auth_ids) >= BRUTE_FORCE_FAILED_AUTH_THRESHOLD:
            disposition = Disposition.ESCALATE
            summary = (
                f"{len(failed_auth_ids)} failed-authentication events exceed the "
                f"brute-force threshold ({BRUTE_FORCE_FAILED_AUTH_THRESHOLD}); escalate for review."
            )
        else:
            disposition = Disposition.INSUFFICIENT_EVIDENCE
            summary = (
                "Telemetry present but no deterministic rule justifies escalation; "
                "evidence insufficient for a confident disposition."
            )

        return ProviderOutput(
            disposition=disposition,
            summary=summary,
            facts=facts,
            hypotheses=hypotheses,
            unknowns=unknowns,
            recommendations=recommendations,
            model="deterministic-v1",
            usage=ProviderUsage(input_tokens=None, output_tokens=None, cost_usd=0.0),
        )