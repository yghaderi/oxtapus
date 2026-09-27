<div dir="rtl" align="right" markdown="1">

# لاگ و مشاهده‌پذیری

لاگ‌های کتابخونه از logger با نام `oxtapus` استفاده می‌کنن و handler سراسری برنامهٔ تو رو
تغییر نمی‌دن. فیلدهای ساختاریافته قبل از ثبت می‌تونن از helper حذف اطلاعات حساس عبور کنن.

Telemetry به‌صورت پیش‌فرض خاموشه. برنامهٔ میزبان می‌تونه برای شمارنده‌ها و مدت‌زمان‌ها یک
`TelemetrySink` بده. payload کامل، credential، cookie و رمز proxy نباید هیچ‌وقت داخل telemetry
قرار بگیرن.

</div>
