<div dir="rtl" align="right" markdown="1">

# مدل‌سازی مالی با دیتافریم‌های Oxtapus

این راهنما برای کسیه که مفاهیم مالی رو می‌شناسه و می‌خواد با چند خط پایتون دادهٔ تمیز آمادهٔ
مدل بسازه. مثال‌ها با Polars نوشته شدن؛ همهٔ محاسبه‌ها محلی هستن و بعد از دریافت داده به سایت
منبع درخواست تازه‌ای نمی‌زنن.

## بازده ساده و لگاریتمی

```python
import polars as pl
import oxtapus as ox

prices = ox.tsetmc.daily_prices(
    ["فولاد", "فملی", "خودرو"],
    start="1402/10/11",
    end="1404/10/08",
)

returns = prices.sort(["symbol", "trading_date"]).with_columns(
    simple_return=(pl.col("close_price") / pl.col("close_price").shift(1) - 1).over("symbol"),
    log_return=(pl.col("close_price").log() - pl.col("close_price").shift(1).log()).over("symbol"),
)
```

ردیف اول هر نماد بازده نداره و مقدارش `null` می‌مونه؛ Oxtapus و Polars اون رو به صفر تبدیل
نمی‌کنن.

## Rolling Volatility

نمونهٔ زیر برای هر نماد، انحراف معیار بازده لگاریتمی رو از ۳۰ بازده ثبت‌شدهٔ اخیر محاسبه می‌کنه
و بعد با فرض ۲۴۰ روز معاملاتی، نوسان‌پذیری سالانه‌شده رو به دست میاره:

```python
risk = returns.with_columns(
    volatility_30d=pl.col("log_return").rolling_std(window_size=30).over("symbol"),
).with_columns(
    annualized_volatility=pl.col("volatility_30d") * (240**0.5),
)
```

این سالانه‌سازی از قاعدهٔ ریشهٔ دوم زمان استفاده می‌کنه. تعداد مشاهده‌ها و تعداد روزهای
معاملاتی سال رو باید متناسب با بازار و فرض‌های مدل انتخاب کنی.

## ساخت ماتریس بازده برای تحلیل همبستگی یا رگرسیون

```python
return_matrix = (
    returns.select("trading_date", "symbol", "simple_return")
    .pivot(
        index="trading_date",
        on="symbol",
        values="simple_return",
    )
    .sort("trading_date")
)
```

هر ستون حالا بازده یک نماده. قبل از برآورد همبستگی یا برازش مدل، روش برخورد با روزهای بدون
معامله و مقدارهای `null` رو آگاهانه مشخص کن؛ جایگزینی خودکار اون‌ها با صفر معمولاً یک فرض مالی
نادرست وارد مدل می‌کنه.

## هم‌ترازسازی بازده سهم و دلار

```python
usd = (
    ox.tgju.daily_prices("دلار", start="1402/10/11")
    .sort("trading_date")
    .with_columns(
        usd_return=pl.col("close_price") / pl.col("close_price").shift(1) - 1,
    )
    .select("trading_date", "usd_return")
)

foolad = returns.filter(pl.col("symbol") == "فولاد").select("trading_date", "simple_return")

model_frame = foolad.join(usd, on="trading_date", how="inner")
```

اتصال داخلی (`inner join`) فقط تاریخ‌های مشترک رو نگه می‌داره. برای مقایسهٔ بازارهایی با تقویم
معاملاتی متفاوت، این انتخاب معمولاً شفاف‌تر از پرکردن خودکار روزهای بدون مشاهده است.

## نقدشوندگی و اختلاف بهترین قیمت خرید و فروش (Bid–Ask Spread)

```python
book = ox.tsetmc.market_depth("فولاد")

top = (
    book.filter(pl.col("order_book_level") == 1)
    .with_columns(
        spread=pl.col("ask_price") - pl.col("bid_price"),
        mid_price=(pl.col("ask_price") + pl.col("bid_price")) / 2,
    )
    .with_columns(
        relative_spread=pl.col("spread") / pl.col("mid_price"),
    )
)
```

این داده فقط وضعیت دفتر سفارش‌ها در لحظهٔ دریافت رو نشون می‌ده، نه تاریخچهٔ اون رو. برای پژوهش
درون‌روزی باید وضعیت دفتر سفارش‌ها رو در زمان‌های مشخص ذخیره کنی و محدودیت نرخ درخواست منبع رو
رعایت کنی.

## کنترل کیفیت قبل از مدل

```python
from oxtapus import Client

with Client() as client:
    result = client.market.fetch_daily_prices(["فولاد", "خودرو"])

assert result.quality_summary["passed"]
print(result.failures)
print(result.warnings)
```

برای کار پژوهشی بهتره بازهٔ زمانی، نسخهٔ بسته، زمان دریافت، پارامترهای درخواست، نسخهٔ طرح‌واره و
هش یا نسخهٔ فایل ورودی مدل رو کنار نتیجه نگه داری تا تحلیل بعداً قابل‌بازتولید باشه.

</div>
