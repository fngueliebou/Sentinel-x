"""Deterministic, rule-based triage — no LLM (Baseline A).

Transparent and reproducible. Produces a TriageDecision from a NormalizedAlert.
It abstains (INSUFFICIENT_EVIDENCE) when the alert lacks the telemetry needed to
justify a decision, rather than defaulting to dismiss/escalate.
"""

from __future__ import annotations

from sentinelx.schemas import Disposition, NormalizedAlert, Severity, TriageDecision

_SEVERITY_PRIORITY: dict[Severity, int] = {
    Severity.INFO: 10,
    Severity.LOW: 25,
    Severity.MEDIUM: 50,
    Severity.HIGH: 75,
    Severity.CRITICAL: 90,
}

# Count of failed-auth-like events that, on its own, warrants escalation.
_BRUTE_FORCE_THRESHOLD = 5


def _count_failed_auth(alert: NormalizedAlert) -> int:
    n = 0
    for ev in alert.events:
        action = (ev.action or "").lower()
        msg = ev.message.lower()
        if "fail" in action or "failed login" in msg or "authentication failure" in msg:
            n += 1
    return n


def triage(alert: NormalizedAlert) -> TriageDecision:
    matched: list[str] = []

    # No telemetry at all -> cannot justify a decision.
    if not alert.events:
        return TriageDecision(
            disposition=Disposition.INSUFFICIENT_EVIDENCE,
            priority=_SEVERITY_PRIORITY.get(alert.severity, 50),
            rationale="No telemetry events attached; cannot substantiate a disposition.",
            matched_rules=[],
        )

    failed = _count_failed_auth(alert)
    if failed >= _BRUTE_FORCE_THRESHOLD:
        matched.append(f"failed_auth>={_BRUTE_FORCE_THRESHOLD} (observed {failed})")

    if alert.severity in (Severity.HIGH, Severity.CRITICAL):
        matched.append(f"severity>={alert.severity.value}")

    priority = _SEVERITY_PRIORITY.get(alert.severity, 50)
    if failed >= _BRUTE_FORCE_THRESHOLD:
        priority = max(priority, 80)

    if matched:
        disposition = Disposition.ESCALATE
        rationale = "Escalated by deterministic rules: " + "; ".join(matched)
    else:
        # Low signal but telemetry present: a conservative baseline escalates
        # nothing it cannot justify, yet does not claim "benign" either.
        disposition = Disposition.INSUFFICIENT_EVIDENCE
        rationale = "Telemetry present but no escalation rule matched."

    return TriageDecision(
        disposition=disposition,
        priority=priority,
        rationale=rationale,
        matched_rules=matched,
    )
