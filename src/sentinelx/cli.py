"""Command-line entry point.

    python -m sentinelx.cli investigate data/alerts/sample_alert_bruteforce.json
    python -m sentinelx.cli investigate <file> --no-rag
"""

from __future__ import annotations

import argparse
import sys

from sentinelx.pipeline import run_investigation_from_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sentinelx")
    sub = parser.add_subparsers(dest="command", required=True)

    inv = sub.add_parser("investigate", help="Run the end-to-end investigation on an alert file.")
    inv.add_argument("alert_file", help="Path to a JSON alert.")
    inv.add_argument(
        "--no-rag",
        action="store_true",
        help="Disable retrieval (LLM-only ablation, Baseline B).",
    )

    args = parser.parse_args(argv)

    if args.command == "investigate":
        report = run_investigation_from_file(args.alert_file, use_rag=not args.no_rag)
        sys.stdout.write(report.model_dump_json(indent=2))
        sys.stdout.write("\n")
        return 0

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
