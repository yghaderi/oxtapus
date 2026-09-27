<div dir="rtl" align="right" markdown="1">

# کلاینت همگام

وقتی چند درخواست داری، به‌جای صدا زدن میان‌برها برای هر درخواست، یک `Client` بساز. این کار
اتصال‌های شبکه رو دوباره استفاده می‌کنه و تنظیمات همهٔ درخواست‌ها هم یک‌جا می‌مونه.

```python
from oxtapus import Client, Settings

with Client(Settings(concurrency=4)) as client:
    result = client.market.fetch_daily_prices(["فولاد", "خودرو"])
    quote = client.market.quote("فولاد")
    book = client.market.market_depth("فولاد")
    activity = client.market.investor_activity("فولاد")
    info = client.instruments.info("فولاد")
    identity = client.instruments.identity("فولاد")
    board = client.governance.board_members("فولاد")
    usd = client.assets.history("دلار")
    frame = result.to_polars()
```

متدهای ساده مثل `history` و `daily_prices` مستقیماً دیتافریم می‌دن. متدهای `fetch_history` و
`fetch_daily_prices` یک `FetchResult` می‌دن که کنار دیتافریم، فرادادهٔ منبع، تلاش‌های مجدد،
هشدار، کیفیت و `lineage` هم داره.

بهترین روش استفاده از `with` است تا اتصال‌ها در پایان بسته بشن. اگه transport رو خودت به
کلاینت داده باشی، مالکیت و بستن اون هم با خودته.

</div>
