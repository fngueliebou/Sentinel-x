# PROJECT_STATE — SENTINEL-X

Canonical status file (project instructions §7). Updated at each significant step.

- **Date** : 2026-10-17
- **Phase** : construction — first vertical slice delivered.
- **Maturity (conception §4)** : N0 (socle) done; N1–N2 partially present via the
  deterministic provider; **not yet validated on public datasets**.

## Completed (tested)

- Repository skeleton, Python packaging (`pyproject.toml`), `.env.example`,
  `.gitignore`, `docker-compose.yml` (pgvector), `db/init/001_schema.sql` (scaffold).
- Data contracts (Pydantic): alert, event, evidence/citation, report.
- Ingestion → normalization → deterministic triage (A).
- In-memory knowledge store + RAG retrieval with provenance.
- `LLMProvider` abstraction; deterministic provider (default) + anthropic provider
  (optional, untested).
- Investigation orchestration → structured report (facts/hypotheses/unknowns/recos).
- Independent citation verification (dangling citations caught).
- Untrusted-data flagging; injection does not change the stub's decision.
- Evaluation harness: baselines A/B/C + run manifest.
- Scenario ground-truth contract (`schemas/scenario.py`), exported via \`schemas/\_\_init\_\_.py\`, with the first scenario data file (`data/scenarios/scenario_bruteforce.json`) and loader test.
- **34/34 tests pass** (`pytest`). CLI and editable install verified.

## In progress / next candidates

- `docs/THREAT_MODEL.md` (from conception §8) — underpins robustness evaluation.
- ADRs for open decisions D1–D8.

## Not implemented (by design, pending measured need)

- Tool-use investigation step (N3) and independent challenge (N4) → baselines D/E.
- Public-dataset evaluation (GUIDE, AIT) with held-out splits.
- pgvector store wiring (needs embedding-model ADR); FastAPI API; MLOps/observability.
- BM25 scoring (D8); hybrid/rerank retrieval.

## Known limitations

- Default "analyst" is a rule-based stub; no real-LLM quality/robustness measured.
- Retrieval is lexical token-overlap (not BM25/vectors).
- Sample scenarios are a smoke test, not a benchmark.

## Open decisions (see docs)

D1 contribution framing · D2 agent orchestration · D3 vector engine · D4 LLM provider
(v1 = API, local optional) · D5 repo license · D6 "SecAlertBench" (unverified) ·
D7 network datasets scope · D8 BM25 scoring.

## Next immediate task (proposed, not started)

Scenario contract + first scenario done. Next candidates: (a) migrate the two
remaining sample alerts to the Scenario format; (b) dataset manifest system +
reproducible GUIDE subset acquisition (no dataset committed); (c) `docs/THREAT_MODEL.md`.
Awaiting user direction.
