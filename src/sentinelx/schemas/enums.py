"""Controlled vocabularies used across SENTINEL-X contracts."""

from __future__ import annotations

from enum import Enum


class Severity(str, Enum):
    """Severity carried by a raw/normalized alert."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Disposition(str, Enum):
    """Triage disposition.

    ESCALATE / DISMISS mirror the tier-1 close-or-escalate decision. The crucial
    third value, INSUFFICIENT_EVIDENCE, lets the system abstain rather than guess
    (conception v0.2 §8; EVALUATION.md §5).
    """

    ESCALATE = "escalate"
    DISMISS = "dismiss"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class FindingKind(str, Enum):
    """The report separates claim types so a reader (and the verifier) can tell
    a grounded fact from a hypothesis or an open question."""

    FACT = "fact"              # must be supported by >= 1 valid citation
    HYPOTHESIS = "hypothesis"  # plausible, explicitly not asserted as established
    UNKNOWN = "unknown"        # an acknowledged gap ("insufficient evidence")
    RECOMMENDATION = "recommendation"  # suggested next step (read-only / for a human)


class SourceType(str, Enum):
    """Where a piece of evidence comes from."""

    EVENT = "event"          # telemetry event supplied with the alert
    KNOWLEDGE = "knowledge"  # retrieved cyber knowledge (ATT&CK, Sigma, KEV, NVD...)
    ALERT = "alert"          # a field of the alert itself
