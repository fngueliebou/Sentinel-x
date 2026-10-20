#!/usr/bin/env python
"""Descriptive scan of one AIT-ADS Wazuh file against its ground-truth labels.

Streams every alert, labels it benign/attack via the testbed's attack windows,
and prints counts.

IMPORTANT: the figures below are DESCRIPTIVE DATASET STATISTICS (how the data is
composed), not detection performance. There is no model here and nothing is being
predicted; do not read the attack proportion as a precision/recall of any kind.

Usage (from the repo root):
    python scripts/sample_ait_ads.py \
        --alerts data/external/ait-ads/fox_wazuh.json \
        --labels data/external/ait-ads/labels.csv \
        --scenario fox [--limit 100000]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from sentinelx.datasets.ait_ads import summarize_labeled_wazuh
from sentinelx.datasets.ait_ads_labels import load_attack_windows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Descriptive AIT-ADS Wazuh scan against ground-truth labels."
    )
    parser.add_argument("--alerts", type=Path, required=True, help="Path to <testbed>_wazuh.json.")
    parser.add_argument("--labels", type=Path, required=True, help="Path to labels.csv.")
    parser.add_argument("--scenario", required=True, help="Testbed name, e.g. 'fox'.")
    parser.add_argument(
        "--limit", type=int, default=None, help="Stop after N alerts (default: scan all)."
    )
    args = parser.parse_args(argv)

    windows = load_attack_windows(args.labels, args.scenario)
    summary = summarize_labeled_wazuh(args.alerts, windows, limit=args.limit)

    print(f"AIT-ADS  scenario={args.scenario}  source=wazuh")
    print(f"  attack windows loaded: {len(windows)}")
    print(f"  alerts scanned:        {summary.total}")
    if summary.total:
        benign_pct = summary.benign / summary.total
        attack_pct = summary.attack_total / summary.total
        print(f"  benign:                {summary.benign} ({benign_pct:.2%})")
        print(f"  attack (total):        {summary.attack_total} ({attack_pct:.2%})")
        for name, count in sorted(summary.per_attack.items(), key=lambda kv: -kv[1]):
            print(f"      {name}: {count}")
        print(f"  time range: {summary.first_timestamp} .. {summary.last_timestamp}")
    print("  NOTE: descriptive dataset statistics, not detection performance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())