"""Retrieve cyber knowledge for an alert and return it as Evidence.

Provenance is preserved end to end: each retrieved document becomes an Evidence
item carrying its source, ref, url and version, plus the retrieval score.
"""

from __future__ import annotations

from sentinelx.knowledge.base import KnowledgeStore
from sentinelx.schemas import Evidence, NormalizedAlert, SourceType
from sentinelx.security import detect_injection_patterns


def build_query(alert: NormalizedAlert) -> str:
    """Compose a retrieval query from the alert's title, actions and entities.

    Event *messages* are deliberately NOT concatenated verbatim into the query to
    limit the influence of untrusted free text on retrieval; structured action
    labels are used instead.
    """
    parts: list[str] = [alert.title]
    if alert.description:
        parts.append(alert.description)
    actions = {ev.action for ev in alert.events if ev.action}
    parts.extend(sorted(actions))
    parts.extend(alert.entities)
    return " ".join(parts)


def retrieve_knowledge(
    alert: NormalizedAlert, store: KnowledgeStore, top_k: int
) -> list[Evidence]:
    query = build_query(alert)
    scored = store.search(query, top_k=top_k)
    evidence: list[Evidence] = []
    for i, sd in enumerate(scored, start=1):
        doc = sd.document
        evidence.append(
            Evidence(
                id=f"EV-KB-{i}",
                source_type=SourceType.KNOWLEDGE,
                source_ref=f"{doc.source} {doc.source_ref}",
                source_url=doc.source_url,
                source_version=doc.source_version,
                content=f"{doc.title}: {doc.text}",
                score=sd.score,
                untrusted_flags=detect_injection_patterns(doc.text),
            )
        )
    return evidence
