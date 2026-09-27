<div dir="rtl" align="right" markdown="1">

# دریافت گروهی

برای چند نماد، لیست رو در یک درخواست سطح بالا بده:

```python
from oxtapus import Client, Settings

with Client(Settings(concurrency=4)) as client:
    result = client.market.fetch_daily_prices(
        ["فولاد", "خودرو", "فملی", "شپنا"],
        start="۱۴۰۲/۱۰/۱۱",
    )

print(result.data)
print(result.failures)
```

`concurrency` سقف کارهای هم‌زمانه، نه تعداد بی‌نهایت اتصال. در حالت پیش‌فرض `collect`، دادهٔ
نمادهای موفق برمی‌گرده و خطاهای هر آیتم در `result.failures` ثبت می‌شه. حالت `fail_fast` با
اولین خطا متوقف می‌شه.

نسخهٔ sync از thread pool محدود و نسخهٔ async از semaphore استفاده می‌کنه. rate limit منبع
در هر دو مسیر رعایت می‌شه.

</div>
