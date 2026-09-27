<div dir="rtl" align="right" markdown="1">

# دریافت و ذخیره‌سازی افزایشی

`IngestionPipeline` پاسخ خام و تغییرناپذیر Bronze رو نگه می‌داره، رکوردهای Silver رو بر اساس
کلید اصلی merge می‌کنه و در صورت نیاز دیتاست Gold می‌سازه. `CheckpointStore` پارتیشن، checksum
و وضعیت کامل‌شدن رو ثبت می‌کنه تا اجرای دوباره بتونه کار تکراری رو رد کنه.

در replay، داده از Bronze خونده می‌شه، checksum بررسی می‌شه و فقط تبدیل خالص و Gold builder
اجرا می‌شن؛ هیچ درخواست شبکه‌ای زده نمی‌شه.

```python
from oxtapus import Client, Settings

settings = Settings(storage_backend="parquet", data_directory="./market-data")
with Client(settings) as client:
    run = client.ingestion.market_watch(progress=True)
    backfill = client.ingestion.daily_prices(
        ["فولاد", "خودرو"], start="۱۴۰۳/۱۰/۱۲", end="۱۴۰۴/۱۰/۱۰"
    )
```

دستورهای `oxtapus ingest` و `oxtapus backfill` هم همین سرویس‌ها رو صدا می‌زنن، پس رفتار CLI و
API پایتون یکیه.

</div>
