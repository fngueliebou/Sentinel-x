"""Tests for the DatasetManifest contract (schemas/dataset_manifest.py).

Covers: a valid minimal manifest, required fields, invalid values, and — the key
point — that naming a license is NOT the same as verifying it.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from sentinelx.schemas.dataset_manifest import (
    DatasetManifest,
    DatasetRole,
    DatasetStatus,
    LicenseVerification,
)


def _minimal() -> dict:
    """The four required fields only."""
    return {
        "dataset_id": "microsoft-guide",
        "name": "Microsoft GUIDE",
        "roles": ["triage"],
        "status": "considered",
    }


def test_valid_minimal_manifest_builds():
    manifest = DatasetManifest.model_validate(_minimal())
    assert manifest.dataset_id == "microsoft-guide"
    assert manifest.roles == [DatasetRole.TRIAGE]
    assert manifest.status == DatasetStatus.CONSIDERED
    # By default, nothing about the license is asserted as a fact.
    assert manifest.license.name is None
    assert manifest.license.verification == LicenseVerification.UNVERIFIED
    # Optional collections default to empty, independently per instance.
    assert manifest.known_limitations == []
    assert manifest.tags == []


def test_missing_required_status_fails():
    kwargs = _minimal()
    del kwargs["status"]
    with pytest.raises(ValidationError):
        DatasetManifest.model_validate(kwargs)


def test_empty_roles_is_rejected():
    kwargs = _minimal()
    kwargs["roles"] = []  # violates min_length=1
    with pytest.raises(ValidationError):
        DatasetManifest.model_validate(kwargs)


def test_empty_dataset_id_is_rejected():
    kwargs = _minimal()
    kwargs["dataset_id"] = ""  # violates min_length=1
    with pytest.raises(ValidationError):
        DatasetManifest.model_validate(kwargs)


def test_unknown_field_is_rejected():
    kwargs = _minimal()
    kwargs["unexpected_field"] = 1  # violates extra="forbid"
    with pytest.raises(ValidationError):
        DatasetManifest.model_validate(kwargs)


def test_invalid_role_value_is_rejected():
    kwargs = _minimal()
    kwargs["roles"] = ["not_a_role"]  # not a DatasetRole member
    with pytest.raises(ValidationError):
        DatasetManifest.model_validate(kwargs)


def test_naming_a_license_does_not_make_it_verified():
    # A license NAME is filled in, but verification is NOT set: it must stay
    # UNVERIFIED. Naming a license is not the same as verifying it.
    kwargs = _minimal()
    kwargs["license"] = {"name": "CDLA-Permissive-2.0"}
    manifest = DatasetManifest.model_validate(kwargs)
    assert manifest.license.name == "CDLA-Permissive-2.0"
    assert manifest.license.verification == LicenseVerification.UNVERIFIED


def test_verified_license_requires_a_source_url():
    # Claiming VERIFIED without citing where it was verified is rejected.
    kwargs = _minimal()
    kwargs["license"] = {"name": "CDLA-Permissive-2.0", "verification": "verified"}
    with pytest.raises(ValidationError):
        DatasetManifest.model_validate(kwargs)


def test_verified_license_with_source_url_is_accepted():
    kwargs = _minimal()
    kwargs["license"] = {
        "name": "CDLA-Permissive-2.0",
        "verification": "verified",
        "source_url": "https://example.org/license-proof",
    }
    manifest = DatasetManifest.model_validate(kwargs)
    assert manifest.license.verification == LicenseVerification.VERIFIED
    assert manifest.license.source_url