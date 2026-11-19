"""Label-quality diagnostics for AIT-ADS Wazuh alerts.

Purpose: efore training any model, check whether our ground-truth labels are
too easily separable by the detection rules themselves, and how much the
time-window labeling inflates/attributes the attack class.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sentinelx.datasets.ait_ads import iter_labeled_wazuh_alerts
from sentinelx.datasets.ait_ads_labels import AttackWindow

__all__ = ["RuleStat", "RuleDiagnostics", "accumulate_rule_stats", "diagnose_wazuh_rules"]

# If any of these keys appear in a raw record, it would carry an embedded
# per-alert label (e.g. the official event_label). We check this empirically.
_EMBEDDED_LABEL_KEYS = ("label", "event_label", "time_label")
_MISSING = "<missing>"


@dataclass
class RuleStat:
    """Per-rule (by Wazuh rule.id) counts across benign/attack alerts."""

    rule_id: str
    total: int = 0
    benign: int = 0
    attack: int = 0
    descriptions: Counter[str] = field(default_factory=Counter)
    groups: Counter[str] = field(default_factory=Counter)
    per_attack: Counter[str] = field(default_factory=Counter)

    @property
    def description(self) -> str:
        return self.descriptions.most_common(1)[0][0] if self.descriptions else _MISSING

    @property
    def attack_ratio(self) -> float:
        return self.attack / self.total if self.total else 0.0

    @property
    def is_ambiguous(self) -> bool:
        """Fires in both attack and benign periods -> label is not rule-intrinsic."""
        return self.attack > 0 and self.benign > 0


@dataclass
class RuleDiagnostics:
    """Aggregated rule statistics for one labeled Wazuh scan."""

    total: int = 0
    benign: int = 0
    attack: int = 0
    rules: dict[str, RuleStat] = field(default_factory=dict)
    per_attack_totals: Counter[str] = field(default_factory=Counter)
    group_totals: Counter[str] = field(default_factory=Counter)
    embedded_label_present: int = 0
    missing_rule_id: int = 0
    missing_description: int = 0
    missing_groups: int = 0

    def top_rules(self, n: int = 15) -> list[RuleStat]:
        return sorted(self.rules.values(), key=lambda r: r.total, reverse=True)[:n]

    def ambiguous_rules(self) -> list[RuleStat]:
        return sorted(
            (r for r in self.rules.values() if r.is_ambiguous),
            key=lambda r: r.total,
            reverse=True,
        )

    def attack_only_rules(self, threshold: float = 0.99) -> list[RuleStat]:
        return sorted(
            (r for r in self.rules.values() if r.attack and r.attack_ratio >= threshold),
            key=lambda r: r.attack,
            reverse=True,
        )

    def benign_only_rules(self, threshold: float = 0.99) -> list[RuleStat]:
        return sorted(
            (r for r in self.rules.values() if r.benign and (1 - r.attack_ratio) >= threshold),
            key=lambda r: r.benign,
            reverse=True,
        )

    @property
    def attack_alerts_on_benign_capable_rules(self) -> int:
        """Attack-labeled alerts whose rule also fires benign: evidence the label
        is temporal (window co-occurrence), not intrinsic to the rule."""
        return sum(r.attack for r in self.rules.values() if r.benign > 0)


def _extract_rule(record: dict[str, Any]) -> tuple[str | None, str | None, list[str]]:
    """Pull (rule_id, description, groups) from a raw Wazuh record, defensively."""
    rule = record.get("rule") or {}
    rid = rule.get("id")
    rid = rid if isinstance(rid, str) and rid else None
    desc = rule.get("description")
    desc = desc if isinstance(desc, str) and desc else None
    raw_groups = rule.get("groups")
    groups = [g for g in raw_groups if isinstance(g, str)] if isinstance(raw_groups, list) else []
    return rid, desc, groups


def accumulate_rule_stats(
    labeled: Iterable[tuple[dict[str, Any], str | None]],
) -> RuleDiagnostics:
    """Fold (raw_record, attack_label) pairs into a RuleDiagnostics.

    ``attack_label`` is None for benign alerts. Pure and streaming: no file I/O,
    so it is unit-testable with synthetic records.
    """
    diag = RuleDiagnostics()
    for record, label in labeled:
        diag.total += 1
        is_attack = label is not None
        if is_attack:
            diag.attack += 1
            diag.per_attack_totals[label] += 1
        else:
            diag.benign += 1

        if any(key in record for key in _EMBEDDED_LABEL_KEYS):
            diag.embedded_label_present += 1

        rid, desc, groups = _extract_rule(record)
        if rid is None:
            diag.missing_rule_id += 1
        if desc is None:
            diag.missing_description += 1
        if not groups:
            diag.missing_groups += 1

        key = rid if rid is not None else _MISSING
        stat = diag.rules.get(key)
        if stat is None:
            stat = RuleStat(rule_id=key)
            diag.rules[key] = stat
        stat.total += 1
        if is_attack:
            stat.attack += 1
            stat.per_attack[label] += 1
        else:
            stat.benign += 1
        if desc is not None:
            stat.descriptions[desc] += 1
        for group in groups:
            stat.groups[group] += 1
            diag.group_totals[group] += 1

    return diag


def diagnose_wazuh_rules(
    alerts_path: Path | str, windows: list[AttackWindow], *, limit: int | None = None
) -> RuleDiagnostics:
    """Stream a Wazuh file, label via attack windows, and aggregate rule stats."""

    def _labeled() -> Iterator[tuple[dict[str, Any], str | None]]:
        count = 0
        for alert, label in iter_labeled_wazuh_alerts(alerts_path, windows):
            yield alert.raw, label
            count += 1
            if limit is not None and count >= limit:
                return

    return accumulate_rule_stats(_labeled())