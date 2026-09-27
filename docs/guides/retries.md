<div dir="rtl" align="right" markdown="1">

# سیاست تلاش مجدد برای خطاهای موقت

مدیریت تلاش مجدد در لایهٔ انتقال متمرکزه. درخواست‌های امن در خطاهای موقت شبکه و کدهای وضعیت
HTTP شامل 408، 425، 429، 500، 502، 503 و 504 دوباره اجرا می‌شن. اگر سرور سرآیند
`Retry-After` بده همون اولویت داره؛ در غیر این صورت از exponential backoff با full jitter و
سقف مشخص استفاده می‌شه.

```python
from oxtapus import Client, Settings

settings = Settings(
    retry_max_attempts=4,
    retry_base_delay=0.5,
    retry_max_delay=15,
    retry_total_delay_budget=30,
)

with Client(settings) as client:
    result = client.market.fetch_daily_prices(["فولاد", "خودرو"])
```

هر درخواست چرخهٔ تلاش مجدد خودش رو داره؛ شکست یک نماد باعث تکرار درخواست موفق نمادهای دیگه
نمی‌شه. خطای ورودی کاربر، تغییر ناسازگار طرح‌واره و خطای کیفیت داده تکرار نمی‌شن چون موقتی
نیستن.

</div>
