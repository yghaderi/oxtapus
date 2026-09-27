# Changelog

## 1.1.0 — 2026-09-27

- Added one typed `asset_history` API for TGJU-backed histories of `usd_irr`, `nima_usd_irr`,
  `eur_irr`, `emami_gold_coin`, and `half_gold_coin`, with Persian input normalization,
  sync/async parity, schema-drift reporting, quality checks, endpoint evidence, and offline/live
  tests.
- Added verified TSETMC quote, order-book, investor-activity, instrument identity/details, and
  board-member disclosure capabilities, plus a documented inventory of discovered route
  families.
- Expanded the Persian user guide with notebook and financial-modeling examples while keeping
  architecture and development documentation in English.
- Added optional Jalali ``start``/``end`` inputs in several common formats, Persian and Arabic
  digit normalization, explicit validation errors, and conversion through jdatetime.
- Restored the README badges with English labels.

## 1.0.0 — 2026-08-30

Oxtapus 1.0.0 is a complete breaking rewrite. It replaces the entire 0.x API; all former
provider-shaped classes, methods, imports, models, columns, flags, exception behavior, and
compatibility expectations were removed with no aliases or shims.

Added a small capability-oriented sync/async API, HTTPX2-only transport, isolated bounded
retries, truthful progress events, verified endpoint and dataset catalogs, strict instrument
resolution, canonical Polars schemas, Bronze/Silver/Gold replay, memory/Parquet/DuckDB
storage, checkpoints, quality/schema-drift reporting, CLI, English documentation, architecture
contracts, offline tests, and opt-in live canaries.
