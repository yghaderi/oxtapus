<div dir="rtl" align="right" markdown="1">

# دریافت و ذخیره‌سازی افزایشی

`IngestionPipeline` پاسخ خام و تغییرناپذیر رو در لایهٔ Bronze نگه می‌داره، رکوردهای Silver رو
بر اساس کلید اصلی ادغام می‌کنه و در صورت نیاز مجموعه‌دادهٔ Gold می‌سازه. `CheckpointStore`
پارتیشن، checksum و وضعیت کامل‌شدن رو ثبت می‌کنه تا اجرای دوباره از پردازش تکراری رد بشه.

در بازپخش (`replay`)، داده از Bronze خونده می‌شه، checksum بررسی می‌شه و فقط تبدیل‌های خالص و
Gold builder اجرا می‌شن؛ هیچ درخواست شبکه‌ای زده نمی‌شه.

```python
from oxtapus import Client, Settings

settings = Settings(storage_backend="parquet", data_directory="./market-data")
with Client(settings) as client:
    run = client.ingestion.market_watch(progress=True)
    backfill = client.ingestion.daily_prices(
        ["فولاد", "خودرو"], start="1403/10/12", end="1404/10/10"
    )
```

دستورهای `oxtapus ingest` و `oxtapus backfill` هم همین سرویس‌ها رو صدا می‌زنن، پس رفتار CLI و
API پایتون یکیه.

</div>
