# Changelog

## 1.2.0 — 2026-09-27

- Replaced ambiguous root shortcuts with explicit ``oxtapus.tsetmc`` and ``oxtapus.tgju``
  source namespaces; both expose ``daily_prices`` and no compatibility aliases remain.
- Grouped CLI fetch commands by source under ``fetch tsetmc`` and ``fetch tgju``.
- Reorganized the Python API reference by source and capability, and linked packaged project
  copy to the generated Sphinx site instead of raw documentation source files.
- Restored concise Persian API summaries from the 0.4.1 documentation where applicable;
  generated signatures, parameters, return descriptions, and types are English and LTR.
- Reviewed Persian financial, statistical, market-data, and data-engineering terminology;
  retained established English terms such as ``Rolling Volatility`` and ``Bid–Ask Spread``
  where a Persian rendering would be unclear.
- Isolated mixed Persian/Latin README text for stable bidirectional rendering and changed
  PyPI-facing documentation links to absolute URLs.
- Changed Jalali dates in user-facing examples to Latin digits while retaining Persian and
  Arabic digit support in the parser.

## 1.1.1 — 2026-09-27

- Removed project-maintainer authorization wording from public project copy.

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
