<div dir="rtl" align="right" markdown="1">

# شروع سریع

## قیمت روزانهٔ سهام

برای گرفتن قیمت‌های روزانه فقط نمادها و بازهٔ تاریخ رو بده:

```python
import oxtapus as ox

prices = ox.daily_prices(
    ["فولاد", "خودرو"],
    start="۱۴۰۳/۱۰/۱۲",
    end="۱۴۰۴/۱۰/۰۸",
    progress=True,
)

print(prices.select("symbol", "trading_date", "close_price", "trade_volume"))
```

خروجی یک `polars.DataFrame` است. اسم ستون‌ها عمداً انگلیسی و `snake_case` هستن تا در کد،
فرمول و ذخیره‌سازی دردسر کمتری داشته باشی.

## دلار و سکه

یک تابع برای هر پنج دارایی داریم؛ فقط اسم دارایی رو عوض کن:

```python
usd = ox.asset_history("دلار", start="۱۴۰۲/۱۰/۱۱")
nima = ox.asset_history("دلار نیما")
eur = ox.asset_history("یورو")
emami = ox.asset_history("سکه امامی")
half = ox.asset_history("نیم‌سکه")
```

فاصلهٔ اضافه، نیم‌فاصله و تفاوت حروف فارسی/عربی مشکلی ایجاد نمی‌کنه. این پنج نام canonical هم
برای کدهای انگلیسی قابل استفاده‌ان:

- `usd_irr`
- `nima_usd_irr`
- `eur_irr`
- `emami_gold_coin`
- `half_gold_coin`

مثلاً این دو درخواست یک دارایی رو می‌گیرن:

```python
first = ox.asset_history("  نیم   سکه ")
second = ox.asset_history("half_gold_coin")
```

اگه نام پشتیبانی نشه، متن خطا هم ورودی خودت رو نشون می‌ده و هم فهرست دارایی‌های مجاز رو.

## اطلاعات لحظه‌ای‌تر بازار

```python
instruments = ox.instrument_search("فولاد")
snapshot = ox.market_watch(["equity", "etf"])
quote = ox.quote("فولاد")
book = ox.market_depth("فولاد")
activity = ox.investor_activity("فولاد")
identity = ox.instrument_identity("فولاد")
board = ox.board_members("فولاد")
chain = ox.option_chain("خودرو")
```

`quote` خلاصهٔ یک‌ردیفی تابلو مثل قیمت اولین، آخرین، پایانی و دامنهٔ روزه. در مقابل،
`market_depth` چند ردیف برمی‌گردونه و هر ردیف یک سطح سفارش خرید و فروشه؛ پس این دو یکی نیستن.

## وقتی جزئیات دریافت مهمه

برای دیدن خطاها، retry، کیفیت داده، نسخهٔ schema و lineage از کلاینت و متد `fetch_...` استفاده
کن:

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
