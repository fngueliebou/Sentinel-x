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
- Scenario ground-truth contract (`schemas/scenario.py`), exported via `schemas/__init__.py`, with three scenario data files (`data/scenarios/`) and a parametrized loader test.
- Cleanup: brute-force threshold centralized in `constants.py` (DRY); deterministic provider emits the scanner-check recommendation once, from scanner knowledge only.
- `DatasetManifest` contract + tests (`schemas/dataset_manifest.py`), exported via `schemas/__init__.py` (license name kept separate from verification status).
- `DATASETS.md`: registry of candidate datasets and RAG knowledge sources — all
  licenses marked **unverified**, **no data downloaded**, nothing verified claimed as fact.
- **48/48 tests pass** (`pytest`), CLI and editable install verified.

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

Dataset manifest contract + registry done (B-1/B-2). Next (B-3): decide which retained datasets to acquire and in what order (GUIDE and AIT are the two core pillars), then build a reproducible acquisition script writing only to the git-ignored `data/external/` (verify licenses first; commit no data). Awaiting user direction on dataset selection.
