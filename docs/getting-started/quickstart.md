# Quickstart

```python
import oxtapus as ox

instruments = ox.instrument_search("فولاد")
prices = ox.daily_prices(["فولاد"], start="2025-01-01", progress=True)
snapshot = ox.market_watch(["equity", "etf"])
chain = ox.option_chain("خودرو")
```

All four values are Polars DataFrames with canonical English columns. Use
`Client.market.fetch_daily_prices` when failures, retries, lineage, quality, or schema
versions matter.
