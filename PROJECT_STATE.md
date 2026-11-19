# PROJECT\_STATE — SENTINEL-X

Canonical status file (project instructions §7). Updated at each significant step.

* **Date** : 2026-11-19
* **Phase** : construction — first vertical slice delivered; first honest evaluation run produced; first N3 (tool-retrieval) reference scenario authored as an artifact.
* **Maturity (conception §4)** : N0 (socle) done; N1–N2 partially present via the deterministic provider; an N3 scenario artifact exists but **tool execution (Baseline D) is not implemented**; **not yet validated on public datasets**.

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
* **Reference scenario #1**`scenario_fox_privesc_shadow.json`: 10 REAL fox/Wazuh events (www-data → su phopkins → sudo root → `cat /etc/shadow`), `expected_disposition=escalate`, `expected_techniques=[T1548.003, T1003.008]` (logged actions). `time_label`. **Not a benchmark.**
* **Reference scenario #2**`scenario_fox_dnsteal.json`: curated 10-event subset of REAL fox `dnsteal` alerts (DNS `.cloud` trigger + TLS anomalies on a *different* host + WordPress attempt + benign Dovecot). `expected_disposition=escalate` (**investigation**, NOT confirmed exfiltration); `expected_techniques=[]` (T1048 / T1071.004 candidates in metadata, IDs verified on MITRE). **Not a benchmark.**
* **Reference scenario #3 (N3)**`scenario_fox_cracking_webmail_cred.json`: curated REAL fox `cracking` window. **Trigger-only initial context** (first auth failure + TLS/level-10 distractors + benign noise); the decisive **failure→success** sequence (christopher.friedman ← 192.168.128.195 on taylorcruz-mail, verified on raw events) is held in `retrievable_events`, to be recovered by tools. **Dual disposition**: `expected_disposition=escalate` (post-investigation) vs `initial_context_disposition=insufficient_evidence` (chosen methodological triage reference). `requires_tool_retrieval=true`. `expected_techniques=[]` (T1110 / T1078 candidates in metadata). **NOT end-to-end runnable until Baseline D.**
* **Scenario schema extended** (`schemas/scenario.py`): `retrievable_events`, `initial_context_disposition`, `requires_tool_retrieval`; validator extended (key-evidence ⊆ initial ∪ retrievable, **no id collision** between the two sets). The validator checks id consistency ONLY — it does NOT claim to validate real tool retrieval.
* **Canonical `expected_techniques` definition** (`docs/EVALUATION.md` §5.2), applied consistently: synthetic scenarios list the techniques they were DESIGNED to represent; real scenarios list ONLY techniques established by telemetry (directly logged, not benign-explained, attribution-independent, not relying on `time_label`); everything else is a candidate in metadata. Fix: `SC-AMBIGUOUS-001``[T1078]`→`[]` (an undecidable scenario establishes nothing).
* **Sample KB extended** (`mitre_sample.json`, `sample-2026-10-22`): `KB-T1548-003`, `KB-T1003-008` — closes the privesc RAG coverage gap (`tests/test_rag_privesc_coverage.py`).
* **Anthropic provider hardened** (`llm/anthropic_provider.py`): explicit parse/validate errors, single-fence unwrap, no silent fallback; 8 mocked unit tests. (Never actually invoked.)
* **Reproducibility**: scenario/eval tests pin `Settings(llm_provider="deterministic")`.
* **Baseline B/C scenario runner** (`scripts/run_scenario.py`, `--rag` for C) + tests.
* **Evaluation harness** (`evals/run_eval.py`) over `data/scenarios/*.json` (single source). **Capability-aware scoring** (`docs/EVALUATION.md` §5.3): A/B/C are TOOL-LESS and evaluate INITIAL-CONTEXT triage only. Each manifest row carries explicit `capability_evaluated`, `ground_truth_basis` (`expected_disposition` for full-context scenarios — unchanged, so historical results stay comparable — or `initial_context_disposition` for tool-retrieval scenarios), and, for tool-retrieval rows, a `match_meaning` note stating a match is correct triage, NOT detection. `retrievable_events` are never fed to the baselines.
* **Latest evaluation run**: A=B=C agree **4/6**. The 3 synthetic cases match; `fox-dnsteal` and `fox-privesc` are missed (stub → `insufficient_evidence` vs `escalate`); `fox-cracking` matches on **initial-context** triage (`insufficient_evidence`) — this is correct triage on a withheld-evidence case, **NOT detection of the compromise** (needs Baseline D). C=B throughout. The 3/5 run on the 5-scenario suite is recorded in `EXP-0001`; the 4/6 run currently lives in the (git-ignored) manifest only — a dedicated `EXP-0002` is not yet written.
* **133/133 tests pass** (`pytest`), validated on Windows.

## In progress / next candidates

* `docs/THREAT_MODEL.md` (from conception §8) — underpins robustness evaluation.
* ADRs for open decisions D1–D8.
* `EXP-0002` to record the current 4/6 run (optional but consistent with §31).

## Not implemented (by design, pending measured need)

* **Tool-use investigation step (N3) → Baseline D**: the `fox-cracking` scenario is an artifact only; no tool layer consumes `retrievable_events` yet. Independent challenge (N4) → Baseline E also absent.
* Real Anthropic provider never actually invoked (no API call made); Baseline B-real NOT YET MEASURED.
* A real BENIGN reference case (`dismiss`): the suite is escalate-heavy (only one synthetic non-escalate case), so specificity / false-positive behaviour on real data is untested.
* Public-dataset evaluation (GUIDE, AIT) with held-out splits.
* pgvector store wiring (needs embedding-model ADR); FastAPI API; MLOps/observability.
* BM25 scoring (D8); hybrid/rerank retrieval.

## Known limitations

* Default "analyst" is a rule-based stub; no real-LLM quality/robustness measured.
* The rule-based triage only reaches the reference disposition on brute-force-shaped signals; it misses both non-brute-force real cases (dnsteal, privesc). Expected for a stub, recorded.
* The `fox-cracking` 4/6 match is initial-context triage, NOT detection; do not read 4/6 as an improvement in detection capability.
* Retrieval is lexical token-overlap (not BM25/vectors).
* The 6-scenario suite is a smoke test, not a benchmark; it is escalate-heavy (a trivial "always escalate" baseline would score high), synthetic cases encode our own assumptions (circularity), and the fox ground truth is a `time_label`, not `event_label`.

## Open decisions (see docs)

D1 contribution framing · D2 agent orchestration · D3 vector engine · D4 LLM provider (v1 = API, local optional) · D5 repo license · D6 "SecAlertBench" (unverified) · D7 network datasets scope · D8 BM25 scoring.

## Next immediate task (proposed, not started)

Three reference scenarios built (incl. one N3 artifact), canonical `expected_techniques` definition applied, capability-aware harness in place (4/6, initial-context only). Open decision for the next increment (to choose): (1) **Baseline D** — a minimal read-only tool layer (`get_authentication_events`, …) + a tool-use investigation step, so the `fox-cracking` N3 scenario becomes runnable end-to-end and its post-investigation `escalate` can actually be reached/evaluated. The concrete next capability level (N3). (2) **Baseline B-real** — wire the real Anthropic provider on ONE scenario for the first non-stub data point (needs API key + small budget; fixed temperature per EVALUATION §7.c). (3) **A real benign reference case** (`dismiss`) to fix the escalate-heavy suite and finally test specificity / false positives on real data (needs a small benign-window sampler, since the extractor only pulls attack windows). (4) **`docs/THREAT_MODEL.md`** + ADRs to pay down documentation/decision debt.
