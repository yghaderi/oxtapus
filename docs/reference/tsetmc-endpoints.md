# TSETMC endpoint catalog

The catalog was verified on 2026-08-29 UTC against the assets and API host used by the live
official website. Evidence includes status, content type and size, semantic checks, negative
identifiers, multiple equities, an ETF, a debt instrument, required browser-origin headers,
and recursive schema fingerprints.

| Capability | Route family | Status | Notes |
|---|---|---|---|
| instrument search | `Instrument/GetInstrumentSearch` | verified | exact match is client-side |
| instrument master | `Instrument/GetInstrumentInfo` | verified | one instrument code |
| daily prices | `ClosingPrice/GetClosingPriceDailyList` | verified | complete history may be large |
| market watch | `ClosingPrice/GetMarketWatch` | verified | equity and ETF paper types |
| option chain | `Instrument/GetInstrumentOptionMarketWatch` | verified | bulk pairs filtered by underlying |
| index levels | `Index/GetIndexB1LastAll` | experimental | not on the public surface |
| market overview | `MarketData/GetMarketOverview` | experimental | not on the public surface |

The packaged `endpoint_catalog.toml` contains exact paths, parameters, envelopes, identifier
types, supported instruments, versions, keys, cadence, pagination, retry safety, headers,
restrictions, observed sizes, timestamps, fingerprints, and limitations. Experimental entries
fail closed unless explicitly requested at the internal catalog boundary.
