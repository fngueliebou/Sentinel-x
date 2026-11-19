from __future__ import annotations

from enum import Enum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DatasetRole(str, Enum):
    """What a dataset is used for in SENTINEL-X evaluation"""

    TRIAGE = "triage"
    INVESTIGATION = "investigation"
    RAG_KNOWLEDGE = "rag_knowledge"
    ROBUSTNESS = "robustness"


class DatasetStatus(str, Enum):
    """Lifecycle stage of a dataset in the project."""

    CONSIDERED = "considered"  # envisagé: noted as a candidate, nothing verified yet
    VERIFIED = "verified"      # provenance/license checked, not downloaded yet
    ACQUIRED = "acquired"      # downloaded locally (into the git-ignored area)
    PREPARED = "prepared"      # preprocessed / splits ready for evaluation


class LicenseVerification(str, Enum):
    """Whether the license has actually been checked — separate from its name."""

    UNVERIFIED = "unverified"        # default: not yet checked
    VERIFIED = "verified"            # checked against a cited source
    NOT_APPLICABLE = "not_applicable"


class LicenseInfo(BaseModel):
    """License name and the status of its verification, deliberately separated."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(
        default=None, description="License identifier, e.g. 'CDLA-Permissive-2.0'. None if unknown."
    )
    verification: LicenseVerification = Field(
        default=LicenseVerification.UNVERIFIED,
        description="Whether the license was actually checked. Defaults to UNVERIFIED.",
    )
    source_url: str | None = Field(
        default=None, description="Where the license was / can be verified."
    )
    notes: str | None = None

    @model_validator(mode="after")
    def _verified_requires_source(self) -> Self:
        # You may only claim VERIFIED if you cite where you verified it. This
        # prevents presenting an assumption ("it's CDLA") as a checked fact.
        if self.verification == LicenseVerification.VERIFIED and not self.source_url:
            raise ValueError("A VERIFIED license must cite a source_url used to verify it.")
        return self


class DatasetManifest(BaseModel):
    """Structured documentation of one dataset"""

    model_config = ConfigDict(extra="forbid")

    # --- Identity (required) ---
    dataset_id: str = Field(..., min_length=1, description="Stable id, e.g. 'microsoft-guide'.")
    name: str = Field(..., description="Human-readable dataset name.")

    # --- Role & lifecycle (required) ---
    roles: list[DatasetRole] = Field(
        ..., min_length=1, description="Intended role(s) in SENTINEL-X evaluation (>= 1)."
    )
    status: DatasetStatus = Field(
        ..., description="Lifecycle stage: considered / verified / acquired / prepared."
    )

    # --- Source & provenance (optional) ---
    source_url: str | None = Field(default=None, description="Official source URL.")
    version: str | None = Field(default=None, description="Dataset version when known.")
    provenance: str | None = Field(
        default=None, description="Short description of where the data comes from."
    )
    citation: str | None = Field(default=None, description="Bibliographic reference / DOI.")

    # --- License (name vs verification kept separate) ---
    # Defaults to an UNVERIFIED LicenseInfo so a manifest always carries an
    # explicit — and honest — license status, even if the author says nothing.
    license: LicenseInfo = Field(
        default_factory=LicenseInfo, description="License name AND its verification status."
    )

    # --- Conditions (optional) ---
    access_conditions: str | None = Field(
        default=None, description="How to obtain it, e.g. 'Kaggle account required'."
    )
    usage_conditions: str | None = Field(
        default=None, description="Permitted uses / restrictions, e.g. 'non-commercial only'."
    )
    redistribution_conditions: str | None = Field(
        default=None, description="e.g. 'do not commit raw data; ship acquisition scripts only'."
    )

    # --- Ground truth (optional) ---
    ground_truth: str | None = Field(
        default=None, description="Labels / ground truth available in the dataset."
    )
    known_limitations: list[str] = Field(
        default_factory=list, description="Known limitations relevant to evaluation."
    )

    # --- Local artifacts, after acquisition (optional) ---
    local_path: str | None = Field(
        default=None, description="Where the data lives locally (under the git-ignored area)."
    )
    local_checksum: str | None = Field(
        default=None, description="Checksum (e.g. sha256) of the acquired data, when available."
    )

    # --- Metadata (optional) ---
    tags: list[str] = Field(default_factory=list, description="Free-form labels.")