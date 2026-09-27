<div dir="rtl" align="right" markdown="1">

# تلاش دوباره و خطاهای موقت

مدیریت retry در لایهٔ انتقال متمرکزه. درخواست‌های امن در خطاهای موقت شبکه و کدهای 408، 425،
429، 500، 502، 503 و 504 دوباره امتحان می‌شن. اگر سرور `Retry-After` بده همون اولویت داره؛
در غیر این صورت فاصلهٔ تلاش‌ها با backoff تصادفی و سقف مشخص زیاد می‌شه.

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

هر درخواست چرخهٔ retry خودش رو داره؛ خراب‌شدن یک نماد باعث تکرار درخواست موفق نمادهای دیگه
نمی‌شه. خطای ورودی کاربر، تغییر ناسازگار schema و خطای کیفیت داده retry نمی‌شن چون موقتی نیستن.

</div>
