"""In-memory knowledge store with transparent lexical (keyword-overlap) scoring.

This is the DEFAULT store for the first slice: it needs no database and no
embedding model, so the pipeline and tests run offline. It is intentionally
simple (lexical token overlap, not BM25, not vector search). The pgvector-backed
store is a separate, not-yet-wired scaffold (D3 / D8).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from sentinelx.knowledge.base import KnowledgeDocument, ScoredDocument

_TOKEN = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> set[str]:
    return set(_TOKEN.findall(text.lower()))


class InMemoryKnowledgeStore:
    """Lexical overlap retrieval over an in-memory document set."""

    def __init__(self, documents: list[KnowledgeDocument]) -> None:
        self._documents = list(documents)
        self._index: dict[str, set[str]] = {
            doc.id: _tokenize(f"{doc.title} {doc.text}") for doc in self._documents
        }

    def all_documents(self) -> list[KnowledgeDocument]:
        return list(self._documents)

    def search(self, query: str, top_k: int) -> list[ScoredDocument]:
        q_tokens = _tokenize(query)
        if not q_tokens:
            return []
        scored: list[ScoredDocument] = []
        for doc in self._documents:
            overlap = q_tokens & self._index[doc.id]
            if not overlap:
                continue
            # Jaccard-like score, stable and in [0, 1].
            score = len(overlap) / len(q_tokens | self._index[doc.id])
            scored.append(ScoredDocument(document=doc, score=round(score, 6)))
        scored.sort(key=lambda s: (s.score, s.document.id), reverse=True)
        return scored[:top_k]


def load_sample_store(
    path: str | Path = "data/knowledge/mitre_sample.json",
) -> InMemoryKnowledgeStore:
    """Load the redistributable sample corpus shipped in data/knowledge/."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    docs = [KnowledgeDocument.model_validate(d) for d in payload["documents"]]
    return InMemoryKnowledgeStore(docs)
