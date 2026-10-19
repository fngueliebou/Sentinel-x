"""Loader for the AIT Alert Data Set (AIT-ADS).

Maps the dataset's raw detector output to SENTINEL-X's ``RawAlert`` contract.
Only the Wazuh producer is handled here for now — its per-record structure is
the cleanest (stable ``id``, ISO ``@timestamp``, rule level/description). AMiner
support (no stable id, epoch timestamps, no severity) comes in a later step.

The alert files are JSON Lines (one JSON object per line) and can reach several
hundred MB, so records are streamed one line at a time — the whole file is never
loaded into memory at once.

All alert content is UNTRUSTED DATA: it is copied into ``RawAlert`` as-is and is
never executed or interpreted as instructions (conception v0.2, §8).
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from typing import Any

from sentinelx.schemas.alert import RawAlert

__all__ = ["wazuh_record_to_raw_alert", "iter_wazuh_alerts"]

_SOURCE = "wazuh"


def _collect_entities(record: dict[str, Any]) -> list[str]:
    """Return the host/ip entities a Wazuh record exposes, de-duplicated and order-stable."""
    predecoder = record.get("predecoder") or {}
    agent = record.get("agent") or {}
    candidates = [predecoder.get("hostname"), agent.get("name"), agent.get("ip")]

    entities: list[str] = []
    for value in candidates:
        if isinstance(value, str) and value and value not in entities:
            entities.append(value)
    return entities


def wazuh_record_to_raw_alert(record: dict[str, Any]) -> RawAlert:
    """Map one parsed Wazuh JSON record to a ``RawAlert``.

    Required fields (``id``, ``@timestamp``) are validated and the function fails
    loudly if they are absent — a malformed record is never silently dropped or
    filled with invented values. Everything else degrades to ``None``/empty, and
    the complete original record is preserved verbatim in ``raw``.
    """
    rule = record.get("rule") or {}

    alert_id = record.get("id")
    if not isinstance(alert_id, str) or not alert_id:
        raise ValueError("Wazuh record has no string 'id'")

    raw_ts = record.get("@timestamp")
    if not isinstance(raw_ts, str) or not raw_ts:
        raise ValueError(f"Wazuh record {alert_id} has no '@timestamp'")
    timestamp = datetime.fromisoformat(raw_ts)  # ISO 8601, e.g. '...Z' (tz-aware)

    description = rule.get("description")
    title = (
        description
        if isinstance(description, str) and description
        else f"wazuh rule {rule.get('id')}"
    )

    level = rule.get("level")
    severity = str(level) if level is not None else None

    return RawAlert(
        id=alert_id,
        source=_SOURCE,
        timestamp=timestamp,
        title=title,
        severity=severity,
        description=record.get("full_log"),
        entities=_collect_entities(record),
        events=[],  # per-event telemetry is reconstructed later from AIT-LDSv2 logs
        raw=record,
    )


def iter_wazuh_alerts(path: Path | str) -> Iterator[RawAlert]:
    """Yield ``RawAlert``s from a Wazuh JSON-Lines file, streamed line by line.

    Blank lines are skipped. The file is never read wholesale, so a 600 MB file
    is processed with flat memory.
    """
    path = Path(path)
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            record = json.loads(stripped)
            yield wazuh_record_to_raw_alert(record)