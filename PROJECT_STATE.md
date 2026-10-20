# PROJECT\_STATE — SENTINEL-X

Canonical status file (project instructions §7). Updated at each significant step.

* **Date** : 2026-10-20
* **Phase** : construction — first vertical slice delivered.
* **Maturity (conception §4)** : N0 (socle) done; N1–N2 partially present via the deterministic provider; **not yet validated on public datasets**.

## Completed (tested)

* Repository skeleton, Python packaging (`pyproject.toml`), `.env.example`, `.gitignore`, `docker-compose.yml` (pgvector), `db/init/001_schema.sql` (scaffold).
* Data contracts (Pydantic): alert, event, evidence/citation, report.
* Ingestion → normalization → deterministic triage (A).
* In-memory knowledge store + RAG retrieval with provenance.
* `LLMProvider` abstraction; deterministic provider (default) + anthropic provider (optional, untested).
* Investigation orchestration → structured report (facts/hypotheses/unknowns/recos).
* Independent citation verification (dangling citations caught).
* Untrusted-data flagging; injection does not change the stub's decision.
* Evaluation harness: baselines A/B/C + run manifest.
* **27/27 tests pass** (`pytest`). CLI and editable install verified.
* Scenario ground-truth contract (`schemas/scenario.py`), exported via `schemas/__init__.py`, with three scenario data files (`data/scenarios/`) and a parametrized loader test.
* Cleanup: brute-force threshold centralized in `constants.py` (DRY); deterministic provider emits the scanner-check recommendation once, from scanner knowledge only.
* `DatasetManifest` contract + tests (`schemas/dataset_manifest.py`), exported via `schemas/__init__.py` (license NAME kept separate from VERIFICATION status).
* `DATASETS.md`: registry of candidate datasets and RAG knowledge sources — all licenses marked **unverified**, **no data downloaded**, nothing verified claimed as fact.
* **48/48 tests pass** (`pytest`), validated on Windows.
* Reproducible content hashing: `datasets/checksum.py` (`sha256_file`/`sha256_dir`, order- and OS-independent) + `scripts/hash_dataset.py` CLI.
* **Dataset licenses verified on primary sources**: GUIDE = `CDLA-Permissive-2.0` (Kaggle); AIT-ADS = `CC BY 4.0` (Zenodo 8263181); AIT-LDSv2 logs = `CC BY-NC-SA 4.0` (Zenodo V2.1). Correction: AIT-ADS is CC BY 4.0, not NC/SA as earlier assumed.
* GUIDE and AIT-ADS **acquired locally** under git-ignored `data/external/` (not committed); AIT-LDSv2 `_no-pcaps` kept outside the repo for now.
* Machine-readable manifests `data/manifests/{ait-ads,microsoft-guide}.json` (status `acquired`, verified licenses + real sha256 of the local copy), validated by `tests/test_manifests_load.py`.
* **AIT-ADS Wazuh loader** (`datasets/ait_ads.py`): streams the JSON-Lines alert files (hundreds of MB) into `RawAlert`s with flat memory; verified on the real 469 MB `fox_wazuh.json`.
* **AIT-ADS ground truth** (`datasets/ait_ads_labels.py`): attack time-windows from `labels.csv`, half-open `[start, end)`, UTC-normalized; pure `attack_at()` labeler.
* **Labeled scan + descriptive summary** (`summarize_labeled_wazuh`) + CLI `scripts/sample_ait_ads.py` — benign/attack composition per testbed (dataset statistics, explicitly **not** detection performance).
* **73/73 tests pass** (`pytest`), validated on Windows.

## In progress / next candidates

* `docs/THREAT_MODEL.md` (from conception §8) — underpins robustness evaluation.
* ADRs for open decisions D1–D8.

## Not implemented (by design, pending measured need)

* Tool-use investigation step (N3) and independent challenge (N4) → baselines D/E.
* Public-dataset evaluation (GUIDE, AIT) with held-out splits.
* pgvector store wiring (needs embedding-model ADR); FastAPI API; MLOps/observability.
* BM25 scoring (D8); hybrid/rerank retrieval.

## Known limitations

* Default "analyst" is a rule-based stub; no real-LLM quality/robustness measured.
* Retrieval is lexical token-overlap (not BM25/vectors).
* Sample scenarios are a smoke test, not a benchmark.

## Open decisions (see docs)

D1 contribution framing · D2 agent orchestration · D3 vector engine · D4 LLM provider (v1 = API, local optional) · D5 repo license · D6 "SecAlertBench" (unverified) · D7 network datasets scope · D8 BM25 scoring.

## Next immediate task (proposed, not started)

AIT-ADS Wazuh loader + ground-truth labeling + descriptive scan done (B-4a/b/c). Next candidates (pick one): (1) run the descriptive scan on the real testbeds to characterize benign/attack composition (dataset stats, no model); (2) feed real AIT-ADS alerts through the existing deterministic triage/investigation pipeline on a held-out split (per `docs/EVALUATION.md`); (3) add AMiner loader support. AMiner is messier (no stable id, epoch timestamps, no severity).
