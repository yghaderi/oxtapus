<div dir="rtl" align="right" markdown="1">

# مدل‌سازی مالی با دیتافریم‌های Oxtapus

این راهنما برای کسیه که مفاهیم مالی رو می‌شناسه و می‌خواد با چند خط پایتون دادهٔ تمیز آمادهٔ
مدل بسازه. مثال‌ها با Polars نوشته شدن؛ همهٔ محاسبه‌ها محلی هستن و بعد از دریافت داده به سایت
منبع درخواست تازه‌ای نمی‌زنن.

## ۱. بازده ساده و لگاریتمی

```python
import polars as pl
import oxtapus as ox

prices = ox.daily_prices(
    ["فولاد", "فملی", "خودرو"],
    start="۱۴۰۲/۱۰/۱۱",
    end="۱۴۰۴/۱۰/۰۸",
)

returns = prices.sort(["symbol", "trading_date"]).with_columns(
    simple_return=(pl.col("close_price") / pl.col("close_price").shift(1) - 1).over("symbol"),
    log_return=(pl.col("close_price").log() - pl.col("close_price").shift(1).log()).over("symbol"),
)
```

ردیف اول هر نماد بازده نداره و مقدارش `null` می‌مونه؛ Oxtapus و Polars اون رو به صفر تبدیل
نمی‌کنن.

## ۲. نوسان متحرک

نمونهٔ زیر انحراف معیار ۳۰ مشاهده‌ای بازده لگاریتمی و نسخهٔ سالانه‌شده با فرض ۲۴۰ روز معاملاتی
رو می‌سازه:

```python
risk = returns.with_columns(
    volatility_30d=pl.col("log_return").rolling_std(window_size=30).over("symbol"),
).with_columns(
    annualized_volatility=pl.col("volatility_30d") * (240**0.5),
)
```

این عدد صرفاً یک تبدیل آماریه؛ انتخاب پنجره و تعداد روزهای سال باید با بازار و مدل خودت سازگار
باشه.

## ۳. ساخت جدول عریض برای همبستگی یا رگرسیون

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

هر ستون حالا بازده یک نماده. قبل از محاسبهٔ همبستگی یا آموزش مدل، سیاست برخورد با روزهای تعطیل
و مقدارهای `null` رو آگاهانه مشخص کن؛ صفرکردن خودکار معمولاً فرض مالی نادرستی وارد مدل می‌کنه.

## ۴. ترکیب سهم با دلار و سکه

```python
usd = (
    ox.asset_history("دلار", start="۱۴۰۲/۱۰/۱۱")
    .sort("trading_date")
    .with_columns(
        usd_return=pl.col("close_price") / pl.col("close_price").shift(1) - 1,
    )
    .select("trading_date", "usd_return")
)

foolad = returns.filter(pl.col("symbol") == "فولاد").select("trading_date", "simple_return")

model_frame = foolad.join(usd, on="trading_date", how="inner")
```

`inner join` فقط تاریخ‌های مشترک رو نگه می‌داره. این رفتار برای مقایسهٔ بازارهایی با تقویم متفاوت
معمولاً شفاف‌تر از پرکردن خودکار فاصله‌هاست.

## ۵. نقدشوندگی و فاصلهٔ سفارش‌ها

```python
book = ox.market_depth("فولاد")

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

این snapshot لحظهٔ دریافت رو نشون می‌ده، نه تاریخچهٔ کامل دفتر سفارش. برای پژوهش درون‌روزی باید
خودت snapshotها رو در زمان‌های مشخص ذخیره کنی و محدودیت نرخ منبع رو رعایت کنی.

## ۶. کنترل کیفیت قبل از مدل

```python
from oxtapus import Client

with Client() as client:
    result = client.market.fetch_daily_prices(["فولاد", "خودرو"])

assert result.quality_summary["passed"]
print(result.failures)
print(result.warnings)
```

برای کار پژوهشی بهتره بازهٔ زمانی، نسخهٔ پکیج، زمان دریافت، query، schema version و هش یا نسخهٔ
فایل ورودی مدل رو کنار نتیجه نگه داری تا تحلیل بعداً قابل‌بازسازی باشه.

</div>
