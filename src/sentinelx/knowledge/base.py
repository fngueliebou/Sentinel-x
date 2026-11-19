"""Knowledge store interface and document contract.

The interface is deliberately small so a pgvector-backed store (scaffolded in
pgvector_store.py) can replace the in-memory one without touching callers (D3).
Every document carries provenance (source, ref, url, version) so retrieval can
always answer "where did this come from?"
"""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    source: str
    source_ref: str
    source_url: str | None = None
    source_version: str | None = None
    title: str
    text: str


class ScoredDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document: KnowledgeDocument
    score: float = Field(..., description="Higher = more relevant.")


class KnowledgeStore(Protocol):
    """Minimal retrieval interface."""

    def search(self, query: str, top_k: int) -> list[ScoredDocument]:
        """Return up to top_k documents relevant to the query, most relevant first."""
        ...

    def all_documents(self) -> list[KnowledgeDocument]:
        ...
