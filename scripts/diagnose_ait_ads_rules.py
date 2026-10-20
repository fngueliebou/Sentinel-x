#!/usr/bin/env python
"""Rule-composition diagnostic for one AIT-ADS Wazuh file vs its time-window labels.

Goal: check, BEFORE any modeling, whether the (reconstructed time_label) classes
are trivially separable by the Wazuh rules, and how much the window labeling
attributes 'attack' to background noise.

These are LABEL-QUALITY / DATASET statistics, NOT detection performance. Our
labels are a time_label (alert timestamp within an attack window); the official
per-event event_label is not in the distributed dataset and is not used here.

Usage (from the repo root):
    python scripts/diagnose_ait_ads_rules.py \
        --alerts data/external/ait-ads/fox_wazuh.json \
        --labels data/external/ait-ads/labels.csv \
        --scenario fox [--top 15] [--limit N]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from sentinelx.datasets.ait_ads_diagnostics import RuleDiagnostics, diagnose_wazuh_rules
from sentinelx.datasets.ait_ads_labels import load_attack_windows


def _pct(part: int, whole: int) -> str:
    return f"{(part / whole):.2%}" if whole else "n/a"


def _print_rule_table(rules, total: int, *, title: str) -> None:
    print(f"\n{title}")
    print(f"  {'rule.id':>8}  {'total':>8}  {'%all':>7}  {'attack':>8}  {'benign':>8}  {'%atk':>6}  description")
    for r in rules:
        print(
            f"  {r.rule_id:>8}  {r.total:>8}  {_pct(r.total, total):>7}  "
            f"{r.attack:>8}  {r.benign:>8}  {_pct(r.attack, r.total):>6}  {r.description[:48]}"
        )


def _report(diag: RuleDiagnostics, scenario: str, top: int) -> None:
    print(f"AIT-ADS rule diagnostic  scenario={scenario}  source=wazuh")
    print("  label basis: reconstructed TIME_LABEL (timestamp in attack window);")
    print("               official event_label NOT available/used.")
    print(f"  alerts:            {diag.total}")
    print(f"  attack (time_label): {diag.attack} ({_pct(diag.attack, diag.total)})")
    print(f"  benign:              {diag.benign} ({_pct(diag.benign, diag.total)})")
    print(f"  embedded per-alert label field present: {diag.embedded_label_present} "
          f"(expected 0 -> confirms no event_label in records)")
    print(f"  missing fields -> rule.id: {diag.missing_rule_id}, "
          f"description: {diag.missing_description}, groups: {diag.missing_groups}")
    print(f"  distinct rule.id: {len(diag.rules)}")

    # Per attack type
    print("\n  attack alerts by type (time_label):")
    for name, count in diag.per_attack_totals.most_common():
        print(f"      {name}: {count} ({_pct(count, diag.attack)} of attack)")

    _print_rule_table(diag.top_rules(top), diag.total, title=f"Top {top} rules overall:")

    # Top groups
    print("\n  Top rule.groups (by alert count):")
    for group, count in diag.group_totals.most_common(top):
        print(f"      {group}: {count} ({_pct(count, diag.total)})")

    # Ambiguous rules (fire in both classes)
    ambiguous = diag.ambiguous_rules()
    amb_attack = sum(r.attack for r in ambiguous)
    print(f"\n  Ambiguous rules (fire in BOTH attack and benign): {len(ambiguous)}")
    _print_rule_table(ambiguous[:top], diag.total, title="   (top ambiguous)")

    # Trivially separating
    attack_only = diag.attack_only_rules()
    benign_only = diag.benign_only_rules()
    print(f"\n  Attack-only rules (>=99% attack): {len(attack_only)} "
          f"covering {sum(r.attack for r in attack_only)} attack alerts")
    _print_rule_table(attack_only[:top], diag.total, title="   (top attack-only)")
    print(f"\n  Benign-only rules (>=99% benign): {len(benign_only)}")

    # Leakage / temporal-label evidence
    leaked = diag.attack_alerts_on_benign_capable_rules
    print("\n  TEMPORAL-LABEL EVIDENCE:")
    print(f"    attack-labeled alerts whose rule ALSO fires benign: {leaked} "
          f"({_pct(leaked, diag.attack)} of attack alerts)")
    print(f"    ambiguous attack alerts total: {amb_attack} ({_pct(amb_attack, diag.attack)} of attack)")
    print("    -> these alerts are 'attack' only because of the time window, not the rule.")

    print("\n  LIMITATIONS:")
    print("    - time_label is temporal co-occurrence, not causation (label noise in positives).")
    print("    - no event_label available -> per-alert causal truth not checked here.")
    print("    - rule.id/description/groups absence counted above; such alerts can't be rule-classified.")
    print("    - descriptive dataset statistics, NOT detection performance.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AIT-ADS Wazuh rule-composition diagnostic.")
    parser.add_argument("--alerts", type=Path, required=True, help="Path to <testbed>_wazuh.json.")
    parser.add_argument("--labels", type=Path, required=True, help="Path to labels.csv.")
    parser.add_argument("--scenario", required=True, help="Testbed name, e.g. 'fox'.")
    parser.add_argument("--top", type=int, default=15, help="Rows per table (default 15).")
    parser.add_argument("--limit", type=int, default=None, help="Stop after N alerts (default: all).")
    args = parser.parse_args(argv)

    windows = load_attack_windows(args.labels, args.scenario)
    diag = diagnose_wazuh_rules(args.alerts, windows, limit=args.limit)
    _report(diag, args.scenario, args.top)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())