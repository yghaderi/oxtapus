# Synchronous client

```python
from oxtapus import Client, Settings

with Client(Settings(concurrency=4)) as client:
    result = client.market.fetch_daily_prices(["فولاد", "خودرو"])
    frame = result.to_polars()
```

Reuse the client for connection pooling. Closing an Oxtapus-created client releases its
transport; injected transports remain caller-owned.
