"""Every committed dataset manifest must be valid under the DatasetManifest contract.

These manifests (data/manifests/*.json) are the machine-readable, committed record
of what has actually been acquired locally. The data itself stays git-ignored; only
the manifest — provenance, verified license, relative path, content checksum — is
versioned. This test guarantees each one stays contract-valid and internally honest.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sentinelx.schemas.dataset_manifest import (
    DatasetManifest,
    DatasetStatus,
    LicenseVerification,
)

_MANIFEST_DIR = Path(__file__).resolve().parents[1] / "data" / "manifests"
_MANIFEST_FILES = sorted(_MANIFEST_DIR.glob("*.json"))


def test_manifest_directory_is_not_empty():
    # Guards against the parametrized test silently collecting zero cases.
    assert _MANIFEST_FILES, f"no manifests found in {_MANIFEST_DIR}"


@pytest.mark.parametrize("path", _MANIFEST_FILES, ids=lambda p: p.stem)
def test_manifest_file_is_valid_and_honest(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    manifest = DatasetManifest.model_validate(data)

    # The file name is the stable id, so the registry stays navigable.
    assert manifest.dataset_id == path.stem
    # These manifests describe data actually downloaded locally.
    assert manifest.status == DatasetStatus.ACQUIRED
    # Local path is repo-relative and points into the git-ignored area.
    assert manifest.local_path is not None
    assert manifest.local_path.startswith("data/external/")
    # A checksum is recorded and explicitly names its algorithm.
    assert manifest.local_checksum is not None
    assert manifest.local_checksum.startswith("sha256:")
    # Honesty invariant: a VERIFIED license must cite where it was verified.
    if manifest.license.verification == LicenseVerification.VERIFIED:
        assert manifest.license.source_url