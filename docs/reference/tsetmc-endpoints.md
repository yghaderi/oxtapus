<div dir="rtl" align="right" markdown="1">

# کاتالوگ endpointهای TSETMC

این کاتالوگ با assetها و میزبان API مورد استفادهٔ سایت رسمی بررسی شده. شواهد شامل status، نوع
و حجم محتوا، بررسی معنایی، شناسهٔ نامعتبر، چند سهم، ETF، ابزار بدهی، headerهای لازم و
fingerprint بازگشتی schema است.

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

فایل `endpoint_catalog.toml` مسیر دقیق، پارامتر، envelope، نوع شناسه، ابزارهای مجاز، نسخه، کلید،
تناوب، pagination، امنیت retry، header، محدودیت، حجم مشاهده‌شده، زمان، fingerprint و مشکل‌های
شناخته‌شده رو ثبت می‌کنه. مسیر experimental در حالت عادی fail-closed است.

[فهرست کامل API](../development/tsetmc-api-inventory.md) همهٔ خانواده‌مسیرهای پیدا‌شده در bundle
رسمی رو فهرست می‌کنه و discovery رو از verification جدا نگه می‌داره. این سند توسعه طبق تصمیم
پروژه انگلیسیه.

</div>
