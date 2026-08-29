# ADR 0004: Bronze, Silver, and Gold

## Context
Auditable ingestion must survive source changes and reproduce canonical data offline.

## Decision
Persist immutable checksummed Bronze, validated canonical Silver, and deterministic curated Gold.

## Alternatives
Persisting only final frames or naming identical copies as layers were considered.

## Consequences
Storage cost increases, while replay, lineage, schema diagnosis, and reproducibility improve.

## Rejected shortcuts
Raw-data loss, secret-bearing metadata, and network-dependent Gold calculations are rejected.

## Operational implications
Retention and filesystem access must be configured; replay verifies checksums before parsing.
