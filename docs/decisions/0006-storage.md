# ADR 0006: Storage abstraction

## Context
Notebooks need no database while platforms need atomic incremental persistence and SQL.

## Decision
Use a narrow storage port with memory, atomic partitioned Parquet, and optional DuckDB adapters.

## Alternatives
A required database, ORM, or one global cache was considered.

## Consequences
Core installation stays light and storage is replaceable.

## Rejected shortcuts
Provider-side writes and non-atomic partition replacement are rejected.

## Operational implications
Primary-key merge, manifests, checksums, partitions, and checkpoints govern reruns.
