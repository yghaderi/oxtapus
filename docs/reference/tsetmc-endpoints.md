<div dir="rtl" align="right" markdown="1">

# کاتالوگ نقطه‌های پایانی TSETMC

این کاتالوگ با فایل‌های ایستای سایت و میزبان API مورد استفادهٔ سایت رسمی بررسی شده. شواهد شامل
کد وضعیت HTTP، نوع و حجم محتوا، بررسی معنایی، شناسهٔ نامعتبر، چند سهم، ETF، ابزار بدهی،
سرآیندهای لازم و fingerprint طرح‌وارهٔ پاسخ است.

| قابلیت | خانوادهٔ مسیر | وضعیت | توضیح |
|---|---|---|---|
| جست‌وجوی ابزار | `Instrument/GetInstrumentSearch` | verified | تطبیق دقیق سمت کلاینت |
| اطلاعات ابزار | `Instrument/GetInstrumentInfo` | verified | یک کد ابزار |
| هویت ابزار | `Instrument/GetInstrumentIdentity` | verified | صنعت و زیرصنعت |
| قیمت روزانه | `ClosingPrice/GetClosingPriceDailyList` | verified | تاریخچهٔ کامل ممکنه حجیم باشه |
| دیده‌بان | `ClosingPrice/GetMarketWatch` | verified | سهم و ETF |
| تابلو | `ClosingPrice/GetClosingPriceInfo` | verified | آخرین رکورد تابلو |
| دفتر سفارش | `BestLimits` | verified | حداکثر پنج سطح خرید/فروش |
| حقیقی/حقوقی | `ClientType/GetClientType` | verified | تعداد و حجم؛ ارزش موجود نیست |
| هیئت‌مدیره | `Codal/GetStatementContentByInsCode/12/0/-1` | verified | JSON همراه XML داخلی |
| زنجیره اختیار | `Instrument/GetInstrumentOptionMarketWatch` | verified | جفت قراردادها با فیلتر دارایی پایه |
| سطح شاخص | `Index/GetIndexB1LastAll` | experimental | هنوز در API عمومی نیست |
| نمای کلی بازار | `MarketData/GetMarketOverview` | experimental | هنوز در API عمومی نیست |

فایل `endpoint_catalog.toml` مسیر دقیق، پارامتر، ساختار پاسخ، نوع شناسه، ابزارهای مجاز، نسخه،
کلید، تناوب، صفحه‌بندی، ایمنی تلاش مجدد، سرآیند، محدودیت، حجم مشاهده‌شده، زمان، fingerprint و
مشکل‌های شناخته‌شده رو ثبت می‌کنه. مسیر experimental در حالت عادی fail-closed است.

[فهرست کامل API](../development/tsetmc-api-inventory.md) همهٔ خانواده‌مسیرهای پیدا‌شده در
bundle رسمی رو فهرست می‌کنه و مرحلهٔ کشف رو از راستی‌آزمایی جدا نگه می‌داره. این سند توسعه طبق
تصمیم پروژه انگلیسیه.

</div>
