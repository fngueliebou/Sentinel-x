"""Baseline configurations (EVALUATION.md §3).

For the first slice three configs are runnable offline:

- A  : deterministic triage, NO LLM.
- B  : LLM (default: deterministic stub), NO retrieval.
- C  : LLM (default: deterministic stub) + RAG.

D (LLM+RAG+tools) and E (LLM+RAG+tools+independent verification) are defined in
the protocol but NOT YET IMPLEMENTED as runnable baselines (no tool-execution
step yet). They are listed here as placeholders so the harness shape is stable.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Baseline:
    key: str
    label: str
    uses_llm: bool
    uses_rag: bool
    implemented: bool


BASELINES: dict[str, Baseline] = {
    "A": Baseline("A", "Deterministic triage (no LLM)", False, False, True),
    "B": Baseline("B", "LLM only (no RAG)", True, False, True),
    "C": Baseline("C", "LLM + RAG", True, True, True),
    "D": Baseline("D", "LLM + RAG + tools", True, True, False),
    "E": Baseline("E", "LLM + RAG + tools + independent verification", True, True, False),
}
