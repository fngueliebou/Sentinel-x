"""Deterministic normalization of a RawAlert into a NormalizedAlert.

No model, no network: a pure function. Severity strings are mapped onto the
controlled vocabulary; unmapped or absent values are recorded in `missing_fields`
rather than guessed.
"""

from __future__ import annotations

from sentinelx.schemas import NormalizedAlert, RawAlert, Severity

# Common severity spellings seen across detectors -> controlled vocabulary.
_SEVERITY_MAP: dict[str, Severity] = {
    "info": Severity.INFO,
    "informational": Severity.INFO,
    "low": Severity.LOW,
    "minor": Severity.LOW,
    "medium": Severity.MEDIUM,
    "moderate": Severity.MEDIUM,
    "warning": Severity.MEDIUM,
    "high": Severity.HIGH,
    "major": Severity.HIGH,
    "critical": Severity.CRITICAL,
    "severe": Severity.CRITICAL,
}

# Numeric severities (e.g. Wazuh-like levels 0-15) bucketed onto the vocabulary.
def _map_numeric(value: str) -> Severity | None:
    try:
        n = int(value)
    except (TypeError, ValueError):
        return None
    if n <= 3:
        return Severity.LOW
    if n <= 7:
        return Severity.MEDIUM
    if n <= 11:
        return Severity.HIGH
    return Severity.CRITICAL


def _map_severity(raw: str | None) -> tuple[Severity, bool]:
    """Return (severity, was_mapped). Falls back to MEDIUM and flags it as missing."""
    if raw is None:
        return Severity.MEDIUM, False
    key = raw.strip().lower()
    if key in _SEVERITY_MAP:
        return _SEVERITY_MAP[key], True
    numeric = _map_numeric(key)
    if numeric is not None:
        return numeric, True
    # Unknown label: do not guess a specific level; use MEDIUM and record the gap.
    return Severity.MEDIUM, False


def normalize_alert(raw: RawAlert) -> NormalizedAlert:
    severity, mapped = _map_severity(raw.severity)

    missing: list[str] = []
    if not mapped:
        missing.append("severity")
    if not raw.description:
        missing.append("description")
    if not raw.entities:
        missing.append("entities")
    if not raw.events:
        missing.append("events")

    return NormalizedAlert(
        id=raw.id,
        source=raw.source,
        timestamp=raw.timestamp,
        title=raw.title,
        description=raw.description,
        severity=severity,
        entities=list(raw.entities),
        events=list(raw.events),
        missing_fields=missing,
    )
