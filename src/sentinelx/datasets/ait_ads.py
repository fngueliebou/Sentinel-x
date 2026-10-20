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
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from sentinelx.datasets.ait_ads_labels import AttackWindow, attack_at
from sentinelx.schemas.alert import RawAlert

__all__ = [
    "wazuh_record_to_raw_alert",
    "iter_wazuh_alerts",
    "iter_labeled_wazuh_alerts",
    "iter_alerts_for_attacks",
    "ScanSummary",
    "summarize_labeled_wazuh",
]

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


def iter_labeled_wazuh_alerts(
    path: Path | str, windows: list[AttackWindow]
) -> Iterator[tuple[RawAlert, str | None]]:
    """Yield ``(alert, attack_label)`` for each Wazuh alert in ``path``.

    ``attack_label`` is the attack name whose window contains the alert's
    timestamp, or ``None`` when the alert is benign (outside every window).
    """
    for alert in iter_wazuh_alerts(path):
        yield alert, attack_at(windows, alert.timestamp)


def iter_alerts_for_attacks(
    path: Path | str,
    windows: list[AttackWindow],
    attacks: set[str] | None = None,
) -> Iterator[tuple[RawAlert, str]]:
    """Yield ``(alert, attack_name)`` only for alerts labeled as an attack.

    Benign alerts are skipped. If ``attacks`` is given, only those attack names
    are kept (e.g. ``{"privilege_escalation", "dnsteal"}``); ``None`` keeps all
    attack-labeled alerts. Streaming, so a 600 MB file is scanned with flat memory.
    """
    for alert, label in iter_labeled_wazuh_alerts(path, windows):
        if label is None:
            continue
        if attacks is not None and label not in attacks:
            continue
        yield alert, label


@dataclass
class ScanSummary:
    """Descriptive counts from a labeled scan of one Wazuh file.

    These are DATASET statistics (how the data is composed), not detection
    performance — there is no model here, nothing is being predicted.
    """

    total: int
    benign: int
    per_attack: dict[str, int]
    first_timestamp: datetime | None
    last_timestamp: datetime | None

    @property
    def attack_total(self) -> int:
        return self.total - self.benign


def summarize_labeled_wazuh(
    path: Path | str, windows: list[AttackWindow], *, limit: int | None = None
) -> ScanSummary:
    """Stream a Wazuh file, label each alert, and return descriptive counts.

    ``limit`` stops after N alerts (quick look); ``None`` scans the whole file.
    Streaming keeps memory flat regardless of file size.
    """
    total = 0
    benign = 0
    per_attack: Counter[str] = Counter()
    first_ts: datetime | None = None
    last_ts: datetime | None = None

    for alert, label in iter_labeled_wazuh_alerts(path, windows):
        total += 1
        moment = alert.timestamp
        if first_ts is None or moment < first_ts:
            first_ts = moment
        if last_ts is None or moment > last_ts:
            last_ts = moment
        if label is None:
            benign += 1
        else:
            per_attack[label] += 1
        if limit is not None and total >= limit:
            break

    return ScanSummary(
        total=total,
        benign=benign,
        per_attack=dict(per_attack),
        first_timestamp=first_ts,
        last_timestamp=last_ts,
    )