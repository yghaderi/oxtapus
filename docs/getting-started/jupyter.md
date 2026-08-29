# Jupyter in five minutes

1. Install with `%pip install oxtapus` and restart the kernel once.
2. Run `import oxtapus as ox`.
3. Fetch `df = ox.daily_prices(["فولاد", "خودرو"], progress=True)`.
4. Explore with `df.group_by("symbol").agg(pl.col("close_price").last())`.
5. For native async, use top-level `await`:

```python
from oxtapus import AsyncClient

async with AsyncClient() as client:
    df = await client.market.daily_prices(["فولاد", "خودرو"], progress=True)
```

No event-loop patch or runner is needed. Progress uses a line-oriented renderer that works in
terminals and notebook output cells.
