<div dir="rtl" align="right" markdown="1">

# تاریخچهٔ ارز و سکه از TGJU

همهٔ دارایی‌ها با یک تابع گرفته می‌شن:

```python
import oxtapus as ox

frame = ox.tgju.daily_prices("دلار", start="1402/10/11", end="1404/10/08")
```

## دارایی‌های پشتیبانی‌شده

| نام فارسی | کد استاندارد | شناسهٔ داخلی منبع |
|---|---|---|
| دلار آزاد | `usd_irr` | `price_dollar_rl` |
| دلار نیما | `nima_usd_irr` | `nima_sell_usd` |
| یورو | `eur_irr` | `price_eur` |
| سکه امامی | `emami_gold_coin` | `sekee` |
| نیم‌سکه | `half_gold_coin` | `nim` |

شناسهٔ داخلی منبع برای شفافیت و `lineage` در جدول اومده، اما ورودی API عمومی نیست. ورودی
عمومی یا نام فارسیه یا کد استاندارد.

## نرمال‌سازی نام فارسی

این ورودی‌ها همگی بدون حساسیت به فاصله و نیم‌فاصله تشخیص داده می‌شن:

```python
ox.tgju.daily_prices("نیم سکه")
ox.tgju.daily_prices("نیم‌سکه")
ox.tgju.daily_prices("  نیم   سکه  ")

ox.tgju.daily_prices("سکه امامی")
ox.tgju.daily_prices("سکه‌امامی")
```

شکل عربی «ی» و «ک»، فاصلهٔ غیرقابل‌شکستن و فاصله‌های تکراری هم نرمال می‌شن. نام مبهم «سکه»
قبول نمی‌شه چون مشخص نمی‌کنه منظور کدوم نوع سکه است.

## خروجی خطای قابل‌فهم

اگر چیزی مثل `"طلای آب شده"` بدی، درخواست شبکه‌ای زده نمی‌شه. خطا مقدار اصلی واردشده و هر
پنج دارایی مجاز رو نمایش می‌ده تا بتونی ورودی رو اصلاح کنی.

## مسیر پیشرفته

```python
from oxtapus import Client

with Client() as client:
    result = client.assets.fetch_history("یورو", start="1402/10/11")

print(result.data)
print(result.retrieved_at)
print(result.source_schema_version)
print(result.quality_summary)
```

نقطهٔ پایانی فقط برای همین پنج نگاشت تأییدشده در دسترسه و URL یا شناسهٔ دلخواه نمی‌پذیره.
شرایط استفاده و بازنشر داده‌ها رو باید جداگانه با مقررات منبع و نوع کاربرد خودت تطبیق بدی.

برای استفاده از خط فرمان هم همین ورودی‌ها معتبرن:

```bash
oxtapus fetch tgju daily-prices 'دلار نیما' --start 1403/10/12
```

</div>
