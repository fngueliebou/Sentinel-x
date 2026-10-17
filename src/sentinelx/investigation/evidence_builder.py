"""Turn alert telemetry events into addressable Evidence items.

Each event becomes an Evidence with a stable id (EV-EVENT-i). Injection-like
patterns in the event message are flagged for visibility (never acted upon).
"""

from __future__ import annotations

from sentinelx.schemas import Evidence, NormalizedAlert, SourceType
from sentinelx.security import detect_injection_patterns


def build_event_evidence(alert: NormalizedAlert) -> list[Evidence]:
    evidence: list[Evidence] = []
    for i, ev in enumerate(alert.events, start=1):
        content = f"{ev.timestamp.isoformat()} [{ev.source}] {ev.action or ''} {ev.message}".strip()
        evidence.append(
            Evidence(
                id=f"EV-EVENT-{i}",
                source_type=SourceType.EVENT,
                source_ref=f"event:{ev.id}",
                source_url=None,
                source_version=None,
                content=content,
                score=None,
                untrusted_flags=detect_injection_patterns(ev.message),
            )
        )
    return evidence
