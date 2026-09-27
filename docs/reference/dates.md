<div dir="rtl" align="right" markdown="1">

# ورودی تاریخ

پارامترهای `start` و `end` اختیاری‌اند. حذف هرکدام یعنی آن سمت بازه محدود نمی‌شود:

```python
all_rows = ox.tgju.daily_prices("دلار")
from_date = ox.tgju.daily_prices("دلار", start="1403/10/12")
until_date = ox.tgju.daily_prices("دلار", end="1404/10/08")
```

## قالب‌های پذیرفته‌شده

تاریخ شمسی با رقم‌های فارسی، عربی یا انگلیسی پذیرفته می‌شود:

```python
ox.tgju.daily_prices("یورو", start="1403-10-12")
ox.tgju.daily_prices("یورو", start="1403/10/12")
ox.tgju.daily_prices("یورو", start="1403.10.12")
ox.tgju.daily_prices("یورو", start="14031012")
```

Oxtapus تاریخ شمسی را با `jdatetime` به میلادی تبدیل می‌کند. تاریخ میلادی با همین چهار فرم و
یک شیء `datetime.date` هم پذیرفته می‌شود. سال‌های 1200 تا 1599 شمسی و سال‌های 1800 تا 2199
میلادی در نظر گرفته می‌شوند تا تقویم ورودی مبهم نباشد.

ستون استاندارد `trading_date` از نوع `date` و میلادی است. تاریخ شمسی خام TGJU هم در ستون
`jalali_date` حفظ می‌شود.

## خطای ورودی

روز یا ماه نامعتبر، جداکننده‌های مخلوط و سال خارج از بازه خطای `ValueError` می‌گیرند. متن خطا
نام پارامتر، مقدار واردشده و قالب‌های مجاز را نشان می‌دهد:

```pycon
>>> ox.tgju.daily_prices("دلار", start="1403/13/01")
Traceback (most recent call last):
...
ValueError: Invalid start='1403/13/01'. Use a valid Jalali date ...
```

</div>
