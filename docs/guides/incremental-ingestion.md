# Incremental ingestion

`IngestionPipeline` writes immutable Bronze evidence, merges Silver primary keys, and builds
optional Gold data. `CheckpointStore` atomically records a dataset partition, checksum, and
completion status so a rerun can skip a matching completed partition.

Replay reads Bronze, verifies the payload checksum, reconstructs a `RawResponse`, then invokes
only the fetcher's pure transform and Gold builder. No transport method is called.

```python
from oxtapus import Client, Settings

settings = Settings(storage_backend="parquet", data_directory="./market-data")
with Client(settings) as client:
    run = client.ingestion.market_watch(progress=True)
    backfill = client.ingestion.daily_prices(
        ["فولاد", "خودرو"], start="2025-01-01", end="2025-12-31"
    )
```

The CLI invokes these same services through `oxtapus ingest` and `oxtapus backfill`.
