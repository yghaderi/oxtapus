<div dir="rtl" align="right" markdown="1">

# شروع سریع

## قیمت روزانهٔ سهام

برای گرفتن قیمت‌های روزانه فقط نمادها و بازهٔ تاریخ رو بده:

```python
import oxtapus as ox

prices = ox.tsetmc.daily_prices(
    ["فولاد", "خودرو"],
    start="1403/10/12",
    end="1404/10/08",
    progress=True,
)

print(prices.select("symbol", "trading_date", "close_price", "trade_volume"))
```

خروجی یک `polars.DataFrame` است. اسم ستون‌ها عمداً انگلیسی و `snake_case` هستن تا در کد،
فرمول و ذخیره‌سازی دردسر کمتری داشته باشی.

## دلار و سکه

یک تابع برای هر پنج دارایی داریم؛ فقط اسم دارایی رو عوض کن:

```python
usd = ox.tgju.daily_prices("دلار", start="1402/10/11")
nima = ox.tgju.daily_prices("دلار نیما")
eur = ox.tgju.daily_prices("یورو")
emami = ox.tgju.daily_prices("سکه امامی")
half = ox.tgju.daily_prices("نیم‌سکه")
```

فاصلهٔ اضافه، نیم‌فاصله و تفاوت حروف فارسی/عربی مشکلی ایجاد نمی‌کنه. این پنج کد استاندارد هم
برای ورودی انگلیسی قابل استفاده‌ان:

- `usd_irr`
- `nima_usd_irr`
- `eur_irr`
- `emami_gold_coin`
- `half_gold_coin`

مثلاً این دو درخواست یک دارایی رو می‌گیرن:

```python
first = ox.tgju.daily_prices("  نیم   سکه ")
second = ox.tgju.daily_prices("half_gold_coin")
```

اگه نام پشتیبانی نشه، متن خطا هم ورودی خودت رو نشون می‌ده و هم فهرست دارایی‌های مجاز رو.

## داده‌های جاری بازار

```python
instruments = ox.tsetmc.instrument_search("فولاد")
snapshot = ox.tsetmc.market_watch(["equity", "etf"])
quote = ox.tsetmc.quote("فولاد")
book = ox.tsetmc.market_depth("فولاد")
activity = ox.tsetmc.investor_activity("فولاد")
identity = ox.tsetmc.instrument_identity("فولاد")
board = ox.tsetmc.board_members("فولاد")
chain = ox.tsetmc.option_chain("خودرو")
```

`quote` خلاصهٔ یک‌ردیفی تابلو، شامل قیمت اولین معامله، آخرین معامله، قیمت پایانی و دامنهٔ قیمت
روزانه است. در مقابل،
`market_depth` چند ردیف برمی‌گردونه و هر ردیف یک سطح سفارش خرید و فروشه؛ پس این دو یکی نیستن.

## وقتی فرادادهٔ دریافت مهمه

برای دیدن خطاها، تلاش‌های مجدد، کیفیت داده، نسخهٔ طرح‌واره و `lineage` از کلاینت و متد
`fetch_...` استفاده کن:

```python
from oxtapus import Client

with Client() as client:
    result = client.assets.fetch_history("دلار")

print(result.data)
print(result.provider)
print(result.quality_summary)
print(result.warnings)
```

</div>
