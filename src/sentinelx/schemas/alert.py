"""Alert contracts: the raw input and its normalized form."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from sentinelx.schemas.enums import Severity
from sentinelx.schemas.event import Event


class RawAlert(BaseModel):
    """An alert as ingested, before normalization.

    Permissive on input (extra fields allowed) because sources are heterogeneous.
    All string content is UNTRUSTED DATA.
    """

    model_config = ConfigDict(extra="allow")

    id: str
    source: str = Field(..., description="Detector/producer, e.g. 'suricata', 'wazuh'.")
    timestamp: datetime
    title: str
    severity: str | None = Field(default=None, description="Raw severity label, free-form.")
    description: str | None = None
    entities: list[str] = Field(default_factory=list)
    events: list[Event] = Field(default_factory=list)
    raw: dict[str, Any] = Field(default_factory=dict, description="Original payload, verbatim.")


class NormalizedAlert(BaseModel):
    """Alert after normalization: strict schema, controlled severity."""

    model_config = ConfigDict(extra="forbid")

    id: str
    source: str
    timestamp: datetime
    title: str
    description: str | None = None
    severity: Severity = Field(..., description="Mapped onto the controlled Severity vocabulary.")
    entities: list[str] = Field(default_factory=list)
    events: list[Event] = Field(default_factory=list)
    # Fields that could not be derived are recorded, not invented (conception §8).
    missing_fields: list[str] = Field(
        default_factory=list, description="Expected fields absent from the raw alert."
    )
