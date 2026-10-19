"""Dataset acquisition utilities (provenance, integrity).

This package holds helpers that make an *already downloaded* dataset
reproducible and auditable: content hashing today (`checksum`), manifest
loading next. It is deliberately separate from the top-level `data/` directory
(which stores data, not code) and from `schemas/` (which defines the contracts).
"""