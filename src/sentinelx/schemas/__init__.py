"""Pydantic data contracts for SENTINEL-X.

These schemas are the stable interface between modules. They are defined BEFORE
the components that produce/consume them (conception v0.2, §3). Everything that
crosses a module boundary is a typed, validated object.
"""

from sentinelx.schemas.enums import Disposition, FindingKind, Severity, SourceType
from sentinelx.schemas.alert import RawAlert, NormalizedAlert
from sentinelx.schemas.event import Event
from sentinelx.schemas.evidence import Evidence, Citation
from sentinelx.schemas.report import (
    Finding,
    InvestigationReport,
    TriageDecision,
)

from sentinelx.schemas.scenario import Scenario


__all__ = [
    "Disposition",
    "FindingKind",
    "Severity",
    "SourceType",
    "RawAlert",
    "NormalizedAlert",
    "Event",
    "Evidence",
    "Citation",
    "Finding",
    "InvestigationReport",
    "TriageDecision",
    "Scenario",
]
