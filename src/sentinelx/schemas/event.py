"""Telemetry event contract"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Event(BaseModel):
    """A normalized telemetry event tied to an alert."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Stable id, unique within the investigation.")
    timestamp: datetime
    source: str = Field(..., description="Producing system, e.g. 'auth', 'edr', 'netflow'.")
    entity: str | None = Field(
        default=None, description="Primary entity (user/host/ip) the event concerns."
    )
    action: str | None = Field(default=None, description="What happened, e.g. 'login_failed'.")
    message: str = Field(..., description="Raw event text. UNTRUSTED — treated as data only.")
    attributes: dict[str, Any] = Field(
        default_factory=dict, description="Additional structured fields."
    )
