<div dir="rtl" align="right" markdown="1">

# تاریخچهٔ ارز و سکه از TGJU

همهٔ دارایی‌ها با یک تابع گرفته می‌شن:

```python
import oxtapus as ox

frame = ox.asset_history("دلار", start="۱۴۰۲/۱۰/۱۱", end="۱۴۰۴/۱۰/۰۸")
```

## دارایی‌های پشتیبانی‌شده

| نام فارسی | کد canonical | شناسهٔ داخلی منبع |
|---|---|---|
| دلار آزاد | `usd_irr` | `price_dollar_rl` |
| دلار نیما | `nima_usd_irr` | `nima_sell_usd` |
| یورو | `eur_irr` | `price_eur` |
| سکه امامی | `emami_gold_coin` | `sekee` |
| نیم‌سکه | `half_gold_coin` | `nim` |

شناسهٔ داخلی منبع برای شفافیت و lineage در جدول اومده، اما ورودی API عمومی نیست. ورودی عمومی
یا نام فارسیه یا کد canonical.

## نرمال‌سازی نام فارسی

این ورودی‌ها همگی بدون حساسیت به فاصله و نیم‌فاصله تشخیص داده می‌شن:

```python
ox.asset_history("نیم سکه")
ox.asset_history("نیم‌سکه")
ox.asset_history("  نیم   سکه  ")

ox.asset_history("سکه امامی")
ox.asset_history("سکه‌امامی")
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
    result = client.assets.fetch_history("یورو", start="۱۴۰۲/۱۰/۱۱")

print(result.data)
print(result.retrieved_at)
print(result.source_schema_version)
print(result.quality_summary)
```

endpoint فقط برای همین پنج mapping تأییدشده بازه و URL یا شناسهٔ دلخواه نمی‌پذیره. این اتصال
بر پایهٔ موافقت‌نامهٔ کتبی نگه‌دارندهٔ Oxtapus نگه‌داری می‌شه؛ حقوق استفادهٔ پایین‌دستی از
داده‌ها باید جداگانه با شرایط منبع و کاربرد خودت سازگار باشه.

برای استفاده از خط فرمان هم همین ورودی‌ها معتبرن:

```bash
oxtapus fetch asset-history 'دلار نیما' --start ۱۴۰۳/۱۰/۱۲
```

</div>
