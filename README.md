# SENTINEL-X

Open-source, self-hostable **AI-assisted SOC investigation platform** (early skeleton).

Canonical design: [`docs/architecture/CONCEPTION_DE_REFERENCE.md`](docs/architecture/CONCEPTION_DE_REFERENCE.md) ·
State of the art: [`docs/research/state-of-the-art.md`](docs/research/state-of-the-art.md) ·
Evaluation protocol: [`docs/EVALUATION.md`](docs/EVALUATION.md).

> **Status:** first vertical slice. The end-to-end flow *ingest → normalize →
> retrieve (RAG) → analyze → verified structured report* runs and is covered by
> tests. The default LLM provider is an **offline deterministic stub** (no API key,
> no network) so the slice is reproducible; a real Claude provider exists behind the
> same interface but is **optional and not exercised by the tests**. Nothing here is
> claimed to be production-ready, accurate, or robust — see "What is NOT done".

## What works today (tested)

- Typed data contracts (Pydantic): `RawAlert`, `NormalizedAlert`, `Event`,
  `Evidence`, `Citation`, `InvestigationReport` (facts / hypotheses / unknowns /
  recommendations).
- Ingestion (JSON) → deterministic normalization (controlled severity, missing-field
  tracking).
- Deterministic triage baseline (no LLM) that can **abstain** (`insufficient_evidence`).
- RAG retrieval over a small redistributable sample knowledge corpus, **provenance
  preserved** on every retrieved item.
- Investigation orchestration producing a **structured report**; every `FACT` carries
  a citation.
- **Independent citation verification**: a fabricated/dangling citation is caught and
  the report fails verification.
- **Untrusted-data handling**: injection-like text in event messages is flagged and
  does **not** change the decision (tested against the deterministic provider only).
- Initial evaluation harness with baselines **A** (deterministic), **B** (LLM-only),
  **C** (LLM+RAG) and a run manifest.

27 tests pass (`pytest`). See "What is NOT done" for the limits of these claims.

## Requirements

- Python ≥ 3.11 (developed on 3.13).
- No database or API key needed for the default flow.

## Install & run locally

```bash
# 1. (recommended) virtual environment
python -m venv .venv && source .venv/bin/activate

# 2. install (editable) with dev extras
pip install -e ".[dev]"

# 3. run the test suite
pytest

# 4. run the end-to-end investigation on a sample alert
sentinelx investigate data/alerts/sample_alert_bruteforce.json
# LLM-only ablation (no retrieval, Baseline B):
sentinelx investigate data/alerts/sample_alert_bruteforce.json --no-rag

# 5. run the initial baseline evaluation (writes a manifest to evals/results/)
python -m evals.run_eval
```

Without installing, prefix commands with `PYTHONPATH=src` (e.g.
`PYTHONPATH=src python -m sentinelx.cli investigate <file>`).

### Using a real LLM (optional, untested here)

```bash
pip install -e ".[llm]"
cp .env.example .env
# set in .env:  SENTINELX_LLM_PROVIDER=anthropic
#               SENTINELX_LLM_API_KEY=...   SENTINELX_LLM_MODEL=<pinned-model>
```
The Anthropic provider fences evidence as untrusted data and asks for strict JSON.
Its correctness/robustness are **NOT YET MEASURED**.

### PostgreSQL + pgvector (scaffold only)

`docker-compose.yml` starts `pgvector/pgvector:pg16` and loads `db/init/001_schema.sql`.
It is **not required** by the current pipeline (the default knowledge store is
in-memory). Set `POSTGRES_PASSWORD` in your shell/`.env` before `docker compose up -d`.

## Repository layout

```
src/sentinelx/
  schemas/        data contracts (alert, event, evidence, report, enums)
  ingestion/      load raw alerts (JSON)
  normalization/  RawAlert -> NormalizedAlert
  triage/         deterministic triage baseline (A)
  knowledge/      knowledge store interface + in-memory store (+ pgvector scaffold)
  rag/            retrieval -> Evidence with provenance
  llm/            provider abstraction: deterministic (default) + anthropic (optional)
  security/       untrusted-data handling (injection flagging)
  investigation/  evidence builder, versioned prompt id, orchestration
  verification/   citation/grounding verifier
  pipeline.py     end-to-end entry
  cli.py          `sentinelx investigate <file>`
evals/            baselines A/B/C, scenarios, run manifest writer
tests/            27 tests (schemas, normalization, triage, RAG, verification, injection, e2e)
data/             redistributable samples + manifest only (no large datasets)
docs/             the three canonical reference documents (+ archive)
db/init/          Postgres schema (scaffold)
```

## What is NOT done (honest limits)

- **No real-LLM measurement.** The default "analyst" is a rule-based stub. Injection
  robustness, investigation quality and hallucination rates for an actual LLM are
  **NOT YET MEASURED**.
- **No tool-use step (N3) and no independent challenge (N4) yet.** Baselines **D** and
  **E** are defined in the protocol but not implemented.
- **No public-dataset evaluation yet.** The sample scenarios are a 3-case smoke test,
  not a benchmark. Real evaluation (GUIDE, AIT) follows `docs/EVALUATION.md`.
- **pgvector store, FastAPI API, MLOps/observability**: scaffolded or absent by design
  until a measured need justifies them.
- **Retrieval is lexical token-overlap**, not BM25 and not vector search (D3/D8).
- **License of the repo is undecided** (D5); dataset licenses are documented but no
  large dataset is bundled.

## Security notes

- Logs/events/knowledge are treated as **untrusted data**, never as instructions.
- LLM tools (when added) will be **read-only, least-privilege**; no offensive actions
  or real remediation are performed.
- No secrets are committed; configure via `.env` (git-ignored).
