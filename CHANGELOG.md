# Changelog

## 1.0.0 — 2026-08-30

Oxtapus 1.0.0 is a complete breaking rewrite. It replaces the entire 0.x API; the old
`TSETMC`, `TGJU`, `Fipiran`, and `Rahavard` classes, their methods, imports, models, columns,
flags, exception behavior, and compatibility expectations were removed with no aliases or
shims.

Added a small capability-oriented sync/async API, HTTPX2-only transport, isolated bounded
retries, truthful progress events, verified endpoint and dataset catalogs, strict instrument
resolution, canonical Polars schemas, Bronze/Silver/Gold replay, memory/Parquet/DuckDB
storage, checkpoints, quality/schema-drift reporting, CLI, English documentation, architecture
contracts, offline tests, and opt-in live canaries.
