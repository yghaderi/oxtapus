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
        start="1403/10/12",
        end="1404/10/08",
    )
```

`LocalParquetStorage` فایل‌های فشردهٔ Zstandard رو در پارتیشن‌های Hive-style می‌نویسه، رکوردها
رو بر اساس کلید اصلی ادغام می‌کنه و یک manifest همراه checksum می‌سازه. `DuckDBStorage`
اختیاریه و امکان اجرای SQL محلی روی Parquet رو اضافه می‌کنه.

با متغیر محیطی `OXTAPUS_STORAGE_BACKEND` هم می‌تونی backend رو انتخاب کنی. لایهٔ ذخیره‌سازی
هیچ‌وقت خودش به منبع اینترنتی درخواست نمی‌زنه.

</div>
