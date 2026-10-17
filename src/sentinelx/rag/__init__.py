"""RAG retrieval: turn an alert into a query and fetch knowledge as Evidence."""

from sentinelx.rag.retriever import build_query, retrieve_knowledge

__all__ = ["build_query", "retrieve_knowledge"]
