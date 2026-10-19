"""Tests for reproducible dataset hashing (sentinelx.datasets.checksum).

Fast and self-contained: every tree is built in a pytest tmp_path, so these
never touch the real (multi-GB) datasets under data/external/.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from sentinelx.datasets.checksum import sha256_dir, sha256_file


def test_sha256_file_matches_hashlib(tmp_path: Path):
    payload = b"brute-force\n" * 1000
    f = tmp_path / "alert.json"
    f.write_bytes(payload)
    assert sha256_file(f) == hashlib.sha256(payload).hexdigest()


def test_sha256_file_streaming_is_chunk_size_independent(tmp_path: Path):
    # A few MiB, deliberately not a round multiple of either chunk size.
    payload = b"x" * (3 * (1 << 20) + 7)
    f = tmp_path / "big.bin"
    f.write_bytes(payload)
    assert sha256_file(f, chunk_size=7) == sha256_file(f, chunk_size=1 << 20)


def test_sha256_file_missing_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        sha256_file(tmp_path / "nope.bin")


def _build_tree(base: Path) -> None:
    (base / "sub").mkdir(parents=True)
    (base / "a.txt").write_bytes(b"A")
    (base / "sub" / "b.txt").write_bytes(b"B")


def test_sha256_dir_is_reproducible_across_identical_trees(tmp_path: Path):
    d1 = tmp_path / "d1"
    d2 = tmp_path / "d2"
    d1.mkdir()
    d2.mkdir()
    _build_tree(d1)
    _build_tree(d2)
    assert sha256_dir(d1) == sha256_dir(d2)


def test_sha256_dir_detects_content_change(tmp_path: Path):
    d = tmp_path / "d"
    d.mkdir()
    _build_tree(d)
    before = sha256_dir(d)
    (d / "a.txt").write_bytes(b"CHANGED")
    assert sha256_dir(d) != before


def test_sha256_dir_detects_rename(tmp_path: Path):
    d = tmp_path / "d"
    d.mkdir()
    _build_tree(d)
    before = sha256_dir(d)
    (d / "a.txt").rename(d / "renamed.txt")
    assert sha256_dir(d) != before


def test_sha256_dir_missing_raises(tmp_path: Path):
    with pytest.raises(NotADirectoryError):
        sha256_dir(tmp_path / "nope")