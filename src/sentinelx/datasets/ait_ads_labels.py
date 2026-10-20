"""Ground-truth labels for AIT-ADS: attack time-windows from ``labels.csv``.

``labels.csv`` columns: ``scenario,attack,start,end`` where ``start``/``end`` are
POSIX epoch seconds. An alert is labeled with an attack type when its timestamp
falls inside one of the attack windows for its testbed (``scenario``); otherwise
it is benign (``None``).

Design notes
------------
- Epoch seconds are converted to **timezone-aware UTC** datetimes at load time, so
  they compare directly and unambiguously with alert timestamps (which are tz-aware
  UTC). Using a naive conversion would silently depend on the machine's local time
  zone — wrong on a Paris workstation vs a UTC server.
- Windows are **half-open** ``[start, end)``. Consecutive windows in the dataset
  touch (one window's ``end`` equals the next window's ``start``); half-open
  intervals make the boundary instant belong to exactly one window, so no instant
  is ever labeled with two attacks.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

__all__ = ["AttackWindow", "load_attack_windows", "attack_at"]

_EXPECTED_HEADER = ["scenario", "attack", "start", "end"]


@dataclass(frozen=True)
class AttackWindow:
    """A labeled attack interval for one testbed. Half-open: ``[start, end)``."""

    scenario: str
    attack: str
    start: datetime
    end: datetime

    def contains(self, moment: datetime) -> bool:
        return self.start <= moment < self.end


def load_attack_windows(path: Path | str, scenario: str) -> list[AttackWindow]:
    """Load the attack windows for one testbed (``scenario``) from ``labels.csv``.

    Rows for other scenarios are ignored. Returned windows are sorted by start.
    Raises ``ValueError`` if the CSV header is not the expected one.
    """
    path = Path(path)
    windows: list[AttackWindow] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != _EXPECTED_HEADER:
            raise ValueError(
                f"unexpected labels header {reader.fieldnames!r}, "
                f"expected {_EXPECTED_HEADER!r}"
            )
        for row in reader:
            if row["scenario"] != scenario:
                continue
            start = datetime.fromtimestamp(float(row["start"]), tz=timezone.utc)
            end = datetime.fromtimestamp(float(row["end"]), tz=timezone.utc)
            windows.append(
                AttackWindow(scenario=scenario, attack=row["attack"], start=start, end=end)
            )
    windows.sort(key=lambda w: w.start)
    return windows


def attack_at(windows: list[AttackWindow], moment: datetime) -> str | None:
    """Return the attack name whose window contains ``moment``, or ``None`` if benign.

    With half-open windows, if two windows touch at a boundary the later window
    owns the boundary instant, so no instant maps to two attacks.
    """
    for window in windows:
        if window.contains(moment):
            return window.attack
    return None