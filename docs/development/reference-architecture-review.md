# Reference architecture and license review

Reviewed projects and lessons (no third-party source was copied):

| Project | License observed | Pattern adopted or rejected |
|---|---|---|
| HTTPX2 | BSD-3-Clause | explicit sync/async pooled transport boundary |
| Pydantic | MIT | immutable typed queries/settings |
| yfinance | Apache-2.0 | concise notebook ergonomics; rejected mutable global concurrency |
| AKShare | MIT | simple function discovery; rejected a broad unstable root surface |
| OpenBB | AGPL-3.0 | provider/query/fetcher concepts only; dependency/code rejected |
| dlt | Apache-2.0 | schema contracts and replay concepts; heavy dependency rejected |
| Kedro | Apache-2.0 | catalog and modular pipeline concepts; dependency rejected |
| 5j9/tsetmc | GPL-3.0 | capability inventory only; code copying rejected |
| pytse-client | GPL-3.0 | capability inventory only; code copying rejected |
| mahs4d/tsetmc-api | MIT | endpoint discovery lead only, independently verified |
| tse_tick | MIT | timestamp and tick-domain review |
| tse-market-data | MIT | dataset capability review |

Medallion guidance informed materially distinct Bronze/Silver/Gold layers. Polars lazy scans
and Arrow dataset patterns informed canonical frames and optional conversion. DuckDB's
Parquet/Hive projection and filter pushdown informed the optional SQL facade.
