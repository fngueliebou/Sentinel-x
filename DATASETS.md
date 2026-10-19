# SENTINEL-X — Dataset & knowledge-source registry

Human-readable registry of datasets and knowledge sources **considered** for SENTINEL-X. It mirrors the `DatasetManifest` contract (`src/sentinelx/schemas/dataset_manifest.py`) but in prose. Machine-readable manifests and any acquisition come in later steps.

## Reading rules (honesty labels)

* **Fact labels**: `[VERIFIED]` a primary/official source was checked for this fact · `[AUTHORS]` a figure announced by the dataset's authors, **not** independently reproduced · `[TO CONFIRM]` taken from a secondary source / search result, to be checked on the official page.
* **License policy**: a license name is **not** a verified fact; each is marked **`unverified`** until independently controlled against the official source. **Update (2026-10-19):** AIT-ADS and AIT-LDSv2 licenses have been verified on their official Zenodo pages (§1.2–1.3) and GUIDE on its Kaggle page (CDLA-Permissive-2.0). All three now verified.
* **No large/restricted data is committed.** Downloaded data lives only under the git-ignored `data/external/`; nothing data-heavy enters git. Local acquisition status: GUIDE and AIT-ADS downloaded to `data/external/`; AIT-LDSv2 `_no-pcaps` kept outside the repo for now. Checksums/versions go in the per-dataset manifests (B-3b).

---

## 1. Retained for evaluation (core candidates)

These directly serve the two evaluation families of `docs/EVALUATION.md` (triage T, investigation I).

### 1.1 Microsoft GUIDE — triage / incident prioritization (T)

* **Source**: Kaggle `Microsoft/microsoft-security-incident-prediction`; paper *AI-Driven Guided Response…* (arXiv:2407.09017, DOI 10.1145/3701716.3715209).
* **Content / volume**: `[AUTHORS]` \~1M incidents with client triage labels (TP/BP/FP), 1.6M alerts, >13M evidence rows, 6.1k orgs, 441 ATT&CK techniques; \~2-week window.
* **Role**: triage/prioritization baselines on **real** SOC labels (Baseline A/B/C).
* **Ground truth**: incident-level triage grade by customer analysts. Imperfect (client labels), strong class imbalance.
* **Data type**: real-world SOC incidents (anonymized).
* **License**: `CDLA-Permissive-2.0` — **[VERIFIED]** on the official Kaggle dataset page (License field, [https://cdla.dev/permissive-2-0/](https://cdla.dev/permissive-2-0/)); **verification: verified**. Permissive data license, commercial use allowed.
* **Priority**: **High** — best real triage labels available; permissive license likely.

### 1.2 AIT-ADS — multi-step alerts for investigation (I)

* **Source**: Zenodo record `8263181`; code `github.com/ait-aecid/alert-data-set`; CSET 2024 (DOI 10.1145/3675741.3675748).
* **Content / volume**: `[AUTHORS]` >2.6M alerts, 93 signatures, from Suricata/Wazuh/AMiner over AIT-LDSv2. (A third-party run, PACT arXiv:2605.22324, used a 587,943-alert stream, \~0.99% malicious.)
* **Role**: investigation with event-level ground truth; basis of the Alert-Bench benchmark (AIDA).
* **Ground truth**: event-level attack labels over a multi-step scenario.
* **Data type**: synthetic (lab testbeds).
* **License**: `CC BY 4.0` — **[VERIFIED]** on the official Zenodo page (record 8263181, v1, 2023-08-18, [https://zenodo.org/records/8263181](https://zenodo.org/records/8263181)); **verification: verified**. Attribution only — **no** NonCommercial/ShareAlike constraint on the alerts (corrects an earlier assumption of NC/SA).
* **Priority**: **High** for investigation; mind the NC/SA constraint.

### 1.3 AIT-LDSv2 — detailed logs for context reconstruction (I)

* **Source**: Zenodo DOI 10.5281/zenodo.5789064 (v2.1: 10.5281/zenodo.19483937).
* **Content / volume**: `[AUTHORS]` 8 testbeds; host system logs + network captures; multi-step attack with parameter variation.
* **Role**: reconstruct the context/timeline behind AIT-ADS alerts (feeds I).
* **Ground truth**: labels/scenarios documented by the authors.
* **Data type**: synthetic (lab).
* **License**: `CC BY-NC-SA 4.0` — **[VERIFIED]** on the official Zenodo page (AIT Log Data Set V2.1, v2\_1, 2026-04-09, [https://zenodo.org/records/19483937](https://zenodo.org/records/19483937)); **verification: verified**. **NonCommercial + ShareAlike** → constrains redistribution of **log-derived** artifacts (does **not** affect AIT-ADS, which is CC BY 4.0).
* **Priority**: **High**, paired with AIT-ADS.

### 1.4 CIC-IDS2017 / UNSW-NB15 — network-flow triage baselines (T, complement)

* **Source**: UNB (CIC-IDS2017, cicids site) and UNSW (research.unsw.edu.au UNSW-NB15).
* **Content**: labeled network flows (benign vs attack families).
* **Role**: classic **triage/classification baselines**, network-only; **not** investigation.
* **Ground truth**: flow labels.
* **Data type**: lab-generated network traffic.
* **License**: institutional terms, academic use + citation; **verification: unverified**`[TO CONFIRM]`.
* **Priority**: **Medium** — useful baselines, but network-only and institutional terms.

---

## 2. RAG knowledge sources (NOT evaluation datasets)

These enrich the RAG index. They are **knowledge**, never used to *measure* system performance — a distinction kept explicit so knowledge is not confused with ground truth.


| Source       | Official link                                    | Use                 | License (unverified)              |
| ------------ | ------------------------------------------------ | ------------------- | --------------------------------- |
| MITRE ATT&CK | attack.mitre.org                                 | techniques, mapping | ATT&CK Terms of Use`[TO CONFIRM]` |
| Sigma rules  | github.com/SigmaHQ/sigma                         | detection rules     | DRL / per-repo`[TO CONFIRM]`      |
| CISA KEV     | cisa.gov/known-exploited-vulnerabilities-catalog | exploited CVEs      | US-gov public`[TO CONFIRM]`       |
| NVD          | nvd.nist.gov                                     | CVE metadata        | US-gov public`[TO CONFIRM]`       |

All must be **versioned** when ingested (a knowledge snapshot date), per conception §13.

---

## 3. New exploratory leads (from research, to be assessed)

Honest status: existence `[VERIFIED]` via official links below; **volumes, formats and licenses are `[TO CONFIRM]` on the official pages** — not reproduced here.

### 3.1 LANL cyber datasets (auth / host / network)

1. **Link**: `csr.lanl.gov/data/` — "Unified Host and Network Data Set" (2017, arXiv:1708.07518) and "Comprehensive, Multi-Source Cyber-Security Events" (2015, auth set).
2. **Content/volume/format**: enterprise authentication, process, flow and DNS events over time; **very large** (billions of events across the 2015 set) `[AUTHORS / TO CONFIRM]`; text/CSV.
3. **Role in SENTINEL-X**: event **correlation**, entity resolution, UEBA-like behavior, and **scale** experiments (throughput/latency/memory).
4. **Ground truth**: the 2015 set flags known **red-team** authentication events; sparse labels (not full triage/investigation labels).
5. **Data type**: real enterprise telemetry (anonymized).
6. **License/access**: LANL public research release; terms on csr.lanl.gov; **verification: unverified**`[TO CONFIRM]`.
7. **Resources**: large download + heavy processing; needs chunked/streamed handling.
8. **Limits/overlap/leakage**: anonymized (limited semantics); labels sparse; different schema from our alert model → mapping needed.
9. **Priority**: **Medium-High** for correlation + scale; low for turnkey triage labels.

### 3.2 DARPA OpTC (Operationally Transparent Cyber)

1. **Link**: `github.com/FiveDirections/OpTC-data` ; IEEE-DataPort mirror.
2. **Content/volume/format**: endpoint provenance (eCAR JSON), \~1 week, benign + red-team days; **very large (\~hundreds of GB to \~1TB)**`[TO CONFIRM]`.
3. **Role**: multi-step **investigation**, host-based provenance, attack-chain reconstruction; **scale**.
4. **Ground truth**: documented red-team activity windows.
5. **Data type**: lab/red-team exercise telemetry.
6. **License/access**: DARPA public release; **verification: unverified**`[TO CONFIRM]`.
7. **Resources**: **heavy** (storage + preprocessing); not a first pick for a laptop-scale start.
8. **Limits**: huge; provenance schema far from our alert model; steep ramp-up.
9. **Priority**: **Low now / revisit for scale** once the pipeline is mature.

### 3.3 OTRF Security-Datasets (ex-Mordor)

1. **Link**: `github.com/OTRF/Security-Datasets` (includes APT29 ATT&CK-evals replays).
2. **Content/volume/format**: pre-recorded security events (Windows/Sysmon, etc.) as JSON, **ATT&CK-technique-mapped**, small per scenario `[TO CONFIRM]`.
3. **Role**: investigation + **ATT&CK mapping** ground truth; small, easy to use; good for building realistic scenarios.
4. **Ground truth**: adversary techniques are labeled/mapped per dataset.
5. **Data type**: lab replays of adversary techniques.
6. **License/access**: **ambiguous** — see `OTRF/Security-Datasets` issue #71 (licensing clarification); **verification: unverified**`[TO CONFIRM — licensing unclear]`.
7. **Resources**: light (JSON, small).
8. **Limits**: Windows-centric; licensing clarity needed before any redistribution.
9. **Priority**: **Medium-High** for technique-mapped investigation scenarios — **gated on resolving the license**.

### 3.4 loghub (logpai)

1. **Link**: `github.com/logpai/loghub` ; Zenodo mirrors.
2. **Content/volume/format**: large collection of **system log** datasets (HDFS, BGL, etc.), some with anomaly labels; text.
3. **Role**: log **parsing / anomaly-detection** sub-experiments; feeds ML signal, not SOC triage directly.
4. **Ground truth**: a few sets carry anomaly labels (e.g., HDFS).
5. **Data type**: real system logs (mostly infrastructure, not SOC alerts).
6. **License/access**: per-dataset, several research-only; **verification: unverified**`[TO CONFIRM per dataset]`.
7. **Resources**: moderate.
8. **Limits**: **not SOC-specific**; weak fit for triage/investigation; useful only for log-ML side studies.
9. **Priority**: **Low** — only if we add a log-anomaly ML sub-track.

### 3.5 Splunk BOTS v3

1. **Link**: `github.com/splunk/botsv3`.
2. **Content/format**: SOC exercise data in **Splunk** format (multiple sources).
3. **Role**: investigation practice; but tied to the Splunk ecosystem.
4. **Ground truth**: exercise questions/answers, not per-event labels.
5. **Data type**: lab SOC exercise.
6. **License/access**: Splunk's own terms (not an OSI license); **verification: unverified**`[TO CONFIRM]`.
7. **Resources**: moderate; Splunk-oriented ingestion.
8. **Limits**: Splunk-format coupling; license is vendor terms.
9. **Priority**: **Low** — poor fit for a vendor-neutral, self-hosted design.

### 3.6 AI-agent robustness benchmarks (exploratory)

* General LLM-agent injection/abuse benchmarks exist (e.g., **Agent Security Bench**, **InjecAgent**) but are **not SOC-specific**`[TO CONFIRM]`. For SENTINEL-X, the primary robustness material should remain our **own synthetic adversarial scenarios** (indirect injection in logs/docs, tool abuse, RAG poisoning), which we control and can map to `forbidden_actions`. External benchmarks are a later cross-check, not a core dependency.
* **Priority**: **Low** as a dependency; **own scenarios** stay primary.

---

## 4. Priority summary & decisions


| Dataset                 | Function                    | Priority        | License caution                                                             |
| ----------------------- | --------------------------- | --------------- | --------------------------------------------------------------------------- |
| Microsoft GUIDE         | triage (real labels)        | **High**        | **CDLA-Permissive-2.0**(verified)                                           |
| AIT-ADS + AIT-LDSv2     | investigation + context     | **High**        | AIT-ADS =**CC BY 4.0**(verified); AIT-LDSv2 logs =**CC BY-NC-SA**(verified) |
| LANL                    | correlation + scale         | **Medium-High** | public release — verify                                                    |
| OTRF Security-Datasets  | ATT&CK-mapped investigation | **Medium-High** | **license unclear (issue #71)**                                             |
| CIC-IDS2017 / UNSW-NB15 | network triage baseline     | **Medium**      | institutional terms                                                         |
| DARPA OpTC              | scale / host provenance     | **Low now**     | heavy; verify                                                               |
| loghub                  | log-ML side studies         | **Low**         | per-dataset                                                                 |
| Splunk BOTS v3          | Splunk-format SOC           | **Low**         | vendor terms                                                                |

**Decisions (proposed, to confirm together):**

* **Retain & deepen first**: GUIDE (triage) and AIT-ADS+AIT-LDSv2 (investigation) — our two core, complementary pillars.
* **Deepen next (research/mapping)**: LANL (correlation + scale) and OTRF Security-Datasets (technique-mapped scenarios), the latter **only after** clarifying its license.
* **Set aside for now**: OpTC (revisit for scale), loghub (only if a log-ML track is added), BOTS v3 (vendor coupling), CIC/UNSW (network-only baseline, keep as optional T complement).
* **Robustness**: keep our **own synthetic adversarial scenarios** primary; external agent-injection benchmarks are a later cross-check.

> None of the above is a commitment to download. The next step (B-3) decides which of the retained datasets to acquire and in what order, then builds a reproducible acquisition script that writes only to the git-ignored `data/external/`.
>
