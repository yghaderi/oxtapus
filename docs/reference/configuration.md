# Configuration

Precedence is constructor arguments, `OXTAPUS_` environment variables, then safe defaults.
Nested values use `__`. Examples:

```bash
export OXTAPUS_CONCURRENCY=6
export OXTAPUS_PROGRESS=true
export OXTAPUS_READ_TIMEOUT=45
```

```python
from oxtapus import Settings

settings = Settings(
    concurrency=6,
    max_connections=12,
    requests_per_second=2,
    retry_max_attempts=4,
    storage_backend="parquet",
    data_directory="/srv/oxtapus/data",
    schema_policy="quarantine",
    failure_mode="collect",
    logging_enabled=True,
    telemetry_enabled=False,
)
```

Settings cover provider/endpoint priority, approved base URLs, user agent, HTTP/2, TLS,
proxy, four timeouts, connection limits, concurrency, rate limits, retries, progress, cache,
data/storage/layers, schema and quality policy, failure mode, freshness, logging, and telemetry.
High-level methods reject arbitrary remote hosts.
