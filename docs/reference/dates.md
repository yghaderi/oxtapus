<div dir="rtl" align="right" markdown="1">

# ورودی تاریخ

پارامترهای `start` و `end` اختیاری‌اند. حذف هرکدام یعنی آن سمت بازه محدود نمی‌شود:

```python
all_rows = ox.asset_history("دلار")
from_date = ox.asset_history("دلار", start="۱۴۰۳/۱۰/۱۲")
until_date = ox.asset_history("دلار", end="۱۴۰۴/۱۰/۰۸")
```

## قالب‌های پذیرفته‌شده

تاریخ شمسی با رقم‌های فارسی، عربی یا انگلیسی پذیرفته می‌شود:

```python
ox.asset_history("یورو", start="۱۴۰۳-۱۰-۱۲")
ox.asset_history("یورو", start="1403/10/12")
ox.asset_history("یورو", start="1403.10.12")
ox.asset_history("یورو", start="14031012")
```

Oxtapus تاریخ شمسی را با `jdatetime` به میلادی تبدیل می‌کند. تاریخ میلادی با همین چهار فرم و
یک شیء `datetime.date` هم پذیرفته می‌شود. سال‌های ۱۲۰۰ تا ۱۵۹۹ شمسی و سال‌های ۱۸۰۰ تا ۲۱۹۹
میلادی در نظر گرفته می‌شوند تا تقویم ورودی مبهم نباشد.

ستون canonical به نام `trading_date` از نوع `date` و میلادی است. تاریخ شمسی خام TGJU نیز در
ستون `jalali_date` حفظ می‌شود.

## خطای ورودی

روز یا ماه نامعتبر، جداکننده‌های مخلوط و سال خارج از بازه خطای `ValueError` می‌گیرند. متن خطا
نام پارامتر، مقدار واردشده و قالب‌های مجاز را نشان می‌دهد:

```pycon
>>> ox.asset_history("دلار", start="۱۴۰۳/۱۳/۰۱")
Traceback (most recent call last):
...
ValueError: Invalid start='۱۴۰۳/۱۳/۰۱'. Use a valid Jalali date ...
```

</div>
