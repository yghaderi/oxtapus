<div dir="rtl" align="right" markdown="1">

# راه‌اندازی در Jupyter

## اولین دیتافریم

1. در یک cell بنویس `%pip install oxtapus`.
2. kernel رو یک‌بار restart کن.
3. کد زیر رو اجرا کن:

```python
import polars as pl
import oxtapus as ox

df = ox.daily_prices(["فولاد", "خودرو"], progress=True)
df.head()
```

برای دیدن آخرین قیمت موجود هر نماد:

```python
latest = (
    df.sort("trading_date")
    .group_by("symbol")
    .agg(
        pl.col("trading_date").last(),
        pl.col("close_price").last(),
    )
)
latest
```

## تبدیل به Pandas

اگه ابزار بعدی‌ات Pandas یا کتابخونه‌ای مثل statsmodels است، extra مربوطه رو نصب کن و تبدیل
انجام بده:

```python
%pip install 'oxtapus[pandas]'
```

```python
pandas_df = df.to_pandas()
```

## استفادهٔ async

Jupyter از `await` مستقیم پشتیبانی می‌کنه:

```python
from oxtapus import AsyncClient

async with AsyncClient() as client:
    df = await client.market.daily_prices(["فولاد", "خودرو"], progress=True)
    usd = await client.assets.history("دلار")
```

نیازی به `asyncio.run`، دستکاری event loop یا `nest_asyncio` نیست. نمایش پیشرفت هم در cell
خروجی کار می‌کنه.

</div>
