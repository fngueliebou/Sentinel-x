"""Reproducible content hashing for acquired datasets.

A ``DatasetManifest`` records a ``local_checksum`` so an acquisition can be
*verified* later: re-hash the local copy and compare. The hash must be
reproducible across machines — in particular across the Windows workstation and
the Linux cloud environment — so the directory hash is made independent of
filesystem iteration order and of path-separator style.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

__all__ = ["sha256_file", "sha256_dir"]

# 1 MiB read buffer: large enough to amortise syscalls, small enough that a
# multi-GB file (e.g. GUIDE ~3.5 GB) is never loaded fully into memory.
_CHUNK_SIZE: int = 1 << 20


def sha256_file(path: Path | str, *, chunk_size: int = _CHUNK_SIZE) -> str:
    """Return the hex SHA-256 of a single file, read in streamed chunks.

    Streaming keeps memory flat regardless of file size. The chunk size never
    affects the result (it only changes how many reads happen).
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"not a file: {path}")

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(chunk_size), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_dir(root: Path | str, *, chunk_size: int = _CHUNK_SIZE) -> str:
    """Return a reproducible hex SHA-256 over the *content* of a directory tree.

    The digest folds in every regular file under ``root``:

    - relative paths are normalised to POSIX form (``/``) so Windows and Linux
      agree, and sorted so filesystem iteration order never changes the result;
    - for each file both its relative path AND its own SHA-256 are mixed in, so
      a content edit *and* a rename/move both change the overall digest.

    Known limitation: symlinks are hashed as whatever ``is_file()`` resolves to;
    special files and empty directories contribute nothing on their own.
    """
    root = Path(root)
    if not root.is_dir():
        raise NotADirectoryError(f"not a directory: {root}")

    files = sorted(
        (p for p in root.rglob("*") if p.is_file()),
        key=lambda p: p.relative_to(root).as_posix(),
    )

    outer = hashlib.sha256()
    for file_path in files:
        rel = file_path.relative_to(root).as_posix()
        file_hash = sha256_file(file_path, chunk_size=chunk_size)
        # A NUL byte cannot appear in a path, so this framing is unambiguous:
        # <relpath>\0<filehash>\n  — no two distinct trees can collide on it.
        outer.update(rel.encode("utf-8"))
        outer.update(b"\0")
        outer.update(file_hash.encode("ascii"))
        outer.update(b"\n")
    return outer.hexdigest()