<div dir="rtl" align="right" markdown="1">

# تنظیمات

اولویت تنظیمات به‌ترتیب آرگومان سازنده، متغیرهای محیطی با پیشوند `OXTAPUS_` و بعد مقدارهای
پیش‌فرض امنه. برای مقدارهای تودرتو از `__` استفاده کن. چند نمونه:

```bash
export OXTAPUS_CONCURRENCY=6
export OXTAPUS_PROGRESS=true
export OXTAPUS_READ_TIMEOUT=45
```

```python
from oxtapus import Settings

settings = Settings(
    concurrency=6,
    max_connections=12,
    requests_per_second=2,
    retry_max_attempts=4,
    storage_backend="parquet",
    data_directory="/srv/oxtapus/data",
    schema_policy="quarantine",
    failure_mode="collect",
    logging_enabled=True,
    telemetry_enabled=False,
)
```

تنظیمات شامل URLهای تأییدشده، user agent، HTTP/2، TLS، proxy، timeoutها، سقف اتصال، هم‌زمانی،
محدودیت نرخ درخواست، تلاش مجدد، نمایش پیشرفت، cache، storage، لایه‌های داده، سیاست طرح‌واره و
کیفیت، رفتار خطای گروهی، تازگی داده، logging و telemetry است. متدهای سطح بالا اجازه نمی‌دن یک
host دلخواه به کتابخونه تحمیل بشه.

</div>
