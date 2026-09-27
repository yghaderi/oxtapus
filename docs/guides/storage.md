<div dir="rtl" align="right" markdown="1">

# ذخیره‌سازی

برای تحلیل سریع در نوت‌بوک لازم نیست چیزی تنظیم کنی؛ `MemoryStorage` پیش‌فرضه. برای نگه‌داری
داده روی دیسک می‌تونی Parquet رو انتخاب کنی:

```python
from oxtapus import Client, Settings

settings = Settings(
    storage_backend="parquet",
    data_directory="./market-data",
)

with Client(settings) as client:
    run = client.ingestion.daily_prices(
        ["فولاد", "خودرو"],
        start="۱۴۰۳/۱۰/۱۲",
        end="۱۴۰۴/۱۰/۰۸",
    )
```

`LocalParquetStorage` فایل‌های فشردهٔ Zstandard رو در پارتیشن‌های Hive-style می‌نویسه، کلیدهای
اصلی رو merge می‌کنه و manifest همراه checksum می‌سازه. `DuckDBStorage` اختیاریه و امکان SQL
محلی روی Parquet رو اضافه می‌کنه.

با متغیر محیطی `OXTAPUS_STORAGE_BACKEND` هم می‌تونی backend رو انتخاب کنی. لایهٔ storage هیچ
وقت خودش به منبع اینترنتی درخواست نمی‌زنه.

</div>
