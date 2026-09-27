<div dir="rtl" align="right" markdown="1">

# کلاینت ناهمگام

برای برنامه‌های ناهمگام، وب‌سرویس‌ها یا نوت‌بوک‌هایی که چند درخواست مستقل دارن از
`AsyncClient` استفاده کن:

```python
from oxtapus import AsyncClient

async with AsyncClient() as client:
    result = await client.market.fetch_daily_prices(["فولاد", "خودرو"])
    quote = await client.market.quote("فولاد")
    book = await client.market.market_depth("فولاد")
    board = await client.governance.board_members("فولاد")
    eur = await client.assets.history("یورو")
```

این مسیر به‌صورت native async پیاده‌سازی شده: کنترل هم‌زمانی، محدودیت نرخ درخواست و backoff
همگی ناهمگامن. Oxtapus میان‌بر همگام رو از داخل کد ناهمگام صدا نمی‌زنه و حلقهٔ رویداد
(`event loop`) برنامهٔ تو رو هم کنترل یا دستکاری نمی‌کنه.

برای بستن درست اتصال‌ها از `async with` استفاده کن. در Jupyter می‌تونی همین کد رو با `await`
مستقیم اجرا کنی.

</div>
