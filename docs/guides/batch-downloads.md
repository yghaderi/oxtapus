<div dir="rtl" align="right" markdown="1">

# دریافت گروهی

برای چند نماد، فهرست رو در یک درخواست سطح بالا بده:

```python
from oxtapus import Client, Settings

with Client(Settings(concurrency=4)) as client:
    result = client.market.fetch_daily_prices(
        ["فولاد", "خودرو", "فملی", "شپنا"],
        start="1402/10/11",
    )

print(result.data)
print(result.failures)
```

`concurrency` سقف تعداد کارهای هم‌زمانه، نه تعداد اتصال‌ها. در حالت پیش‌فرض `collect`، دادهٔ
نمادهای موفق برمی‌گرده و خطای هر مورد در `result.failures` ثبت می‌شه. حالت `fail_fast` با
اولین خطا متوقف می‌شه.

نسخهٔ همگام از یک thread pool محدود و نسخهٔ ناهمگام از semaphore استفاده می‌کنه. محدودیت نرخ
درخواست منبع در هر دو مسیر رعایت می‌شه.

</div>
