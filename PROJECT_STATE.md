# PROJECT\_STATE — SENTINEL-X

Canonical status file (project instructions §7). Updated at each significant step.

* **Date** : 2026-10-23
* **Phase** : construction — first vertical slice delivered; first honest evaluation run produced.
* **Maturity (conception §4)** : N0 (socle) done; N1–N2 partially present via the deterministic provider; **not yet validated on public datasets**.

## Completed (tested)

* Repository skeleton, Python packaging (`pyproject.toml`), `.env.example`, `.gitignore`, `docker-compose.yml` (pgvector), `db/init/001_schema.sql` (scaffold).
* Data contracts (Pydantic): alert, event, evidence/citation, report.
* Ingestion → normalization → deterministic triage (A).
* In-memory knowledge store + RAG retrieval with provenance.
* `LLMProvider` abstraction; deterministic provider (default) + anthropic provider.
* Investigation orchestration → structured report (facts/hypotheses/unknowns/recos).
* Independent citation verification (dangling citations caught).
* Untrusted-data flagging; injection does not change the stub's decision.
* Scenario ground-truth contract (`schemas/scenario.py`), exported via `schemas/__init__.py`.
* Cleanup: brute-force threshold centralized in `constants.py` (DRY); deterministic provider emits the scanner-check recommendation once, from scanner knowledge only.
* `DatasetManifest` contract + tests; license NAME kept separate from VERIFICATION status.
* `DATASETS.md`: registry of candidate datasets and RAG knowledge sources.
* Reproducible content hashing: `datasets/checksum.py` + `scripts/hash_dataset.py` CLI.
* **Dataset licenses verified on primary sources**: GUIDE = `CDLA-Permissive-2.0` (Kaggle); AIT-ADS = `CC BY 4.0` (Zenodo 8263181); AIT-LDSv2 logs = `CC BY-NC-SA 4.0` (Zenodo V2.1).
* GUIDE and AIT-ADS **acquired locally** under git-ignored `data/external/`.
* Machine-readable manifests `data/manifests/{ait-ads,microsoft-guide}.json`.
* **AIT-ADS Wazuh loader** (`datasets/ait_ads.py`): streams the JSON-Lines alert files with flat memory; verified on the real 469 MB `fox_wazuh.json`.
* **AIT-ADS ground truth** (`datasets/ait_ads_labels.py`): attack time-windows from `labels.csv`, half-open `[start, end)`, UTC-normalized. **Reconstructed `time_label`**; the official per-event `event_label` is NOT in the Zenodo record and is not used.
* **Rule-composition diagnostic** + CLI; run on fox/Wazuh (462,523 alerts): attack class dominated by `dirb` web scan (98.5%); near-trivial separability / leakage documented in `docs/EVALUATION.md` §5.1. **Dataset statistics, not detection performance.**
* **Attack-phase extractor** (`iter_alerts_for_attacks` + `scripts/extract_ait_ads_attack.py`).
* **Reference scenario #1**`data/scenarios/scenario_fox_privesc_shadow.json`: 10 REAL fox/Wazuh events (www-data → su phopkins → sudo root → `cat /etc/shadow`), `expected_disposition=escalate`, `expected_techniques=[T1548.003, T1003.008]` (observed execution only). Label provenance = `time_label`. **Not a benchmark.**
* **Reference scenario #2**`data/scenarios/scenario_fox_dnsteal.json`: curated 10-event subset of REAL fox alerts from the `dnsteal` window (DNS `.cloud` trigger + TLS anomalies on a *different* host + automated WordPress attempt + benign Dovecot noise). `expected_disposition=escalate` (**investigation**, NOT confirmed exfiltration); `expected_techniques=[]` — candidates T1048 / T1071.004 kept as **hypotheses** in metadata (IDs verified on official MITRE ATT&CK). Source window (381 alerts, 336 benign Dovecot) vs curated subset explicitly documented. **Not a benchmark.**
* **Sample KB extended** (`data/knowledge/mitre_sample.json`, version `sample-2026-10-22`): added `KB-T1548-003` (sudo-to-root) and `KB-T1003-008` (/etc/shadow access) — **closes the earlier RAG coverage gap** on the fox-privesc case. Retrieval coverage asserted by `tests/test_rag_privesc_coverage.py` (T1548.003 and T1003.008 both in top-5).
* **Anthropic provider hardened** (`llm/anthropic_provider.py`): explicit parse/validate errors, single-fence unwrap, no silent deterministic fallback; 8 mocked unit tests.
* **Reproducibility**: scenario/eval tests pin `Settings(llm_provider="deterministic")` so runs never depend on the ambient env / a local `.env`.
* **Baseline B/C scenario runner** (`scripts/run_scenario.py`, `--rag` for C) + tests.
* **Evaluation harness consolidated** on `data/scenarios/*.json` as the single scenario source (replaces the `sample_scenarios.json` pointer list; the `data/alerts/` fixtures remain for unit tests). `evals/run_eval.py` runs A/B/C over all 5 scenarios, records a manifest (`evals/results/`, git-ignored) with per-scenario disposition vs reference, per-baseline agreement, provider/model/seed, prompt version, git commit. Harness test `tests/test_eval_harness.py` (coverage + the C=B disposition-invariance invariant).
* **First honest evaluation run (EXP-0001)**: A=B=C agree **3/5**; the 3 synthetic cases match, **both real fox cases are missed** (stub → `insufficient_evidence` vs reference `escalate`); **C=B** (RAG disposition-invariant). Recorded in `docs/experiments/EXP-0001-reference-triage-baselines.md`. **Descriptive, not performance.**
* **121/121 tests pass** (`pytest`), validated on Windows.

## In progress / next candidates

* `docs/THREAT_MODEL.md` (from conception §8) — underpins robustness evaluation.
* ADRs for open decisions D1–D8.

## Not implemented (by design, pending measured need)

* Tool-use investigation step (N3) and independent challenge (N4) → baselines D/E.
* Real Anthropic provider never actually invoked (no API call made); Baseline B-real NOT YET MEASURED.
* Public-dataset evaluation (GUIDE, AIT) with held-out splits.
* pgvector store wiring (needs embedding-model ADR); FastAPI API; MLOps/observability.
* BM25 scoring (D8); hybrid/rerank retrieval.

## Known limitations

* Default "analyst" is a rule-based stub; no real-LLM quality/robustness measured.
* The rule-based triage only reaches the reference disposition on brute-force-shaped signals; it misses both real reference cases (EXP-0001). Expected for a stub, recorded.
* Retrieval is lexical token-overlap (not BM25/vectors).
* The 5-scenario suite is a smoke test, not a benchmark; synthetic cases encode our own assumptions (circularity) and the fox ground truth is a `time_label`, not `event_label`.

## Open decisions (see docs)

D1 contribution framing · D2 agent orchestration · D3 vector engine · D4 LLM provider (v1 = API, local optional) · D5 repo license · D6 "SecAlertBench" (unverified) · D7 network datasets scope · D8 BM25 scoring.

## Next immediate task (proposed, not started)

Two reference scenarios built, KB coverage closed, harness consolidated, first honest result produced (EXP-0001: stub 3/5, misses both real cases, C=B). Open decision for the next increment (to choose): (1) **Baseline B-real** — wire the real Anthropic provider on ONE scenario to get the first non-stub data point (needs API key + a small budget; fixed temperature per EVALUATION §7.c); this is the actual capability jump the 3/5 result motivates. Or (2) **enlarge the reference suite** — more real AIT scenarios (and a trigger-only + read-only-tools variant for N3) to make the evaluation less dependent on 2 cases. Or (3) **`docs/THREAT_MODEL.md`** + ADRs to pay down documentation/decision debt before the LLM step.
