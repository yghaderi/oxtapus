# Asynchronous client

```python
from oxtapus import AsyncClient

async with AsyncClient() as client:
    result = await client.market.fetch_daily_prices(["فولاد", "خودرو"])
```

The async path uses `httpx2.AsyncClient`, an async semaphore, async rate limiting, and async
backoff. It does not call synchronous shortcuts or control the event loop.
