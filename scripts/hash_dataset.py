"""Compute a reproducible SHA-256 for a dataset file or directory.

Usage (from the repo root):
    python scripts/hash_dataset.py data/external/ait-ads data/external/microsoft-guide

For a directory it prints the content hash (independent of filesystem order and
of OS path separators), the number of regular files, and the total size — the
figures that go into a ``DatasetManifest``. It imports the project's own hashing
functions, so the result is exactly what verification will later recompute.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sentinelx.datasets.checksum import sha256_dir, sha256_file


def _dir_stats(root: Path) -> tuple[int, int]:
    """Return (file count, total bytes) for the regular files under ``root``."""
    files = [p for p in root.rglob("*") if p.is_file()]
    total = sum(p.stat().st_size for p in files)
    return len(files), total


def _human(n: int) -> str:
    """Render a byte count in binary units (KiB/MiB/GiB)."""
    size = float(n)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if size < 1024 or unit == "TiB":
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{n} B"  # unreachable, keeps the type checker happy


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Reproducible SHA-256 for a dataset path (file or directory)."
    )
    parser.add_argument(
        "paths", nargs="+", type=Path, help="File(s) or directory(ies) to hash."
    )
    args = parser.parse_args(argv)

    exit_code = 0
    for path in args.paths:
        if path.is_dir():
            digest = sha256_dir(path)
            count, total = _dir_stats(path)
            print(f"sha256:{digest}  {path.as_posix()}  ({count} files, {_human(total)})")
        elif path.is_file():
            digest = sha256_file(path)
            print(f"sha256:{digest}  {path.as_posix()}  ({_human(path.stat().st_size)})")
        else:
            print(f"ERROR: not found: {path}", file=sys.stderr)
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())