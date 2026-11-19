"""pgvector-backed knowledge store — SCAFFOLD, not yet wired.

Placeholder for the PostgreSQL + pgvector adapter. It is intentionally not
implemented: the in-memory store is the default for the first slice, and a real
vector store requires an embedding-model decision (recorded as an ADR) before it
earns its place. Left here so the interface boundary is visible.
"""

from __future__ import annotations

from sentinelx.knowledge.base import ScoredDocument


class PgVectorKnowledgeStore:  # pragma: no cover - scaffold
    def __init__(self, *args: object, **kwargs: object) -> None:
        raise NotImplementedError(
            "pgvector store is not implemented yet. Use InMemoryKnowledgeStore. "
            "Wiring this requires an embedding-model ADR (see docs/decisions)."
        )

    def search(self, query: str, top_k: int) -> list[ScoredDocument]:  # pragma: no cover
        raise NotImplementedError

    def all_documents(self) -> list:  # pragma: no cover
        raise NotImplementedError
