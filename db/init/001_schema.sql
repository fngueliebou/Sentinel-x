-- SENTINEL-X — initial database schema (SCAFFOLD).
-- Loaded by docker-compose on first DB start. Not yet used by the running pipeline
-- (the default knowledge store is in-memory). Kept minimal and will evolve with an ADR.

CREATE EXTENSION IF NOT EXISTS vector;

-- Knowledge chunks for RAG (provenance preserved on every row).
CREATE TABLE IF NOT EXISTS knowledge_chunk (
    id            TEXT PRIMARY KEY,
    source        TEXT NOT NULL,          -- e.g. "MITRE ATT&CK", "Sigma", "NVD"
    source_ref    TEXT NOT NULL,          -- e.g. technique id "T1110", CVE id, rule id
    source_url    TEXT,
    source_version TEXT,                  -- versioned knowledge is mandatory
    title         TEXT NOT NULL,
    text          TEXT NOT NULL,
    -- embedding dimension is a placeholder; set when the embedding model is chosen (ADR).
    embedding     vector(384)
);

-- Investigation audit trail (one row per run; full traceability).
CREATE TABLE IF NOT EXISTS investigation_run (
    id             TEXT PRIMARY KEY,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    alert_id       TEXT NOT NULL,
    llm_provider   TEXT NOT NULL,
    llm_model      TEXT,
    prompt_version TEXT NOT NULL,
    report_json    JSONB NOT NULL
);
