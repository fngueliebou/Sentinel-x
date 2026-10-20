#!/usr/bin/env python
"""Extract and display the real Wazuh alerts of given attack phase(s) for a testbed.

Purpose: BEFORE designing a grounded investigation scenario, look at the actual
alert content of the high-value, rare phases (e.g. privilege_escalation, dnsteal,
cracking) — so the scenario is built from real evidence, not invented.

This reads only alerts whose (time_label) attack matches the requested phase(s).
It is descriptive inspection, not detection.

Usage (from the repo root):
    python scripts/extract_ait_ads_attack.py \
        --alerts data/external/ait-ads/fox_wazuh.json \
        --labels data/external/ait-ads/labels.csv \
        --scenario fox \
        --attack privilege_escalation --attack dnsteal \
        --limit 20 [--full-log]
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from sentinelx.datasets.ait_ads import iter_alerts_for_attacks
from sentinelx.datasets.ait_ads_labels import load_attack_windows


def _rule(alert) -> dict:
    return alert.raw.get("rule") or {}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract Wazuh alerts for given attack phase(s).")
    parser.add_argument("--alerts", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument(
        "--attack", action="append", default=None,
        help="Attack phase to keep (repeatable). Omit to keep all attack phases.",
    )
    parser.add_argument("--limit", type=int, default=20, help="Max alerts to print (default 20).")
    parser.add_argument("--full-log", action="store_true", help="Also print the full_log line.")
    args = parser.parse_args(argv)

    windows = load_attack_windows(args.labels, args.scenario)
    wanted = set(args.attack) if args.attack else None

    print(f"scenario={args.scenario}  attacks={sorted(wanted) if wanted else 'ALL'}  "
          f"(time_label; descriptive, not detection)")

    shown = 0
    per_attack: Counter[str] = Counter()
    per_rule: Counter[str] = Counter()
    for alert, attack in iter_alerts_for_attacks(args.alerts, windows, wanted):
        per_attack[attack] += 1
        rule = _rule(alert)
        per_rule[str(rule.get("id"))] += 1
        if shown < args.limit:
            print(
                f"\n[{attack}] {alert.timestamp.isoformat()}  id={alert.id}  "
                f"level={rule.get('level')}  rule={rule.get('id')} \"{rule.get('description')}\""
            )
            print(f"    entities={alert.entities}  groups={rule.get('groups')}")
            if args.full_log:
                log = (alert.description or "")[:300]
                print(f"    log: {log}")
            shown += 1

    print("\n--- summary (full match, not just shown) ---")
    for name, count in per_attack.most_common():
        print(f"  {name}: {count}")
    print("  rule.id distribution:")
    for rid, count in per_rule.most_common():
        print(f"      {rid}: {count}")
    print(f"  printed {shown} of {sum(per_attack.values())} matching alerts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())