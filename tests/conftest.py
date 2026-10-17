"""Shared fixtures. Forces the deterministic (offline) provider for all tests."""

from __future__ import annotations

import pytest

from sentinelx.config import Settings
from sentinelx.knowledge import load_sample_store


@pytest.fixture
def settings() -> Settings:
    return Settings(llm_provider="deterministic", retrieval_top_k=5)


@pytest.fixture
def store():
    return load_sample_store("data/knowledge/mitre_sample.json")
