# Dataset catalog

| Dataset | Layer | Primary key | Unit | Update |
|---|---|---|---|---|
| `instrument` | Silver | `tsetmc_instrument_code` | record | daily |
| `daily_price` | Silver | instrument code + trading date | IRR, shares | trading day |
| `market_watch` | Silver | instrument code | IRR, shares | intraday |
| `option_quote` | Silver | instrument code | IRR, contracts | intraday |
| `market_snapshot` | Gold | instrument code | IRR, shares | intraday |
| `option_chain` | Gold | instrument code | IRR, contracts | intraday |

The packaged `data_catalog.toml` is authoritative for ownership, schema version,
partitioning, sorting, freshness, duplicate/null policy, rules, retention, and lineage.
