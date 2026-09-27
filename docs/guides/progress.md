<div dir="rtl" align="right" markdown="1">

# نمایش پیشرفت

برای نمایش سادهٔ پیشرفت در ترمینال یا نوت‌بوک، `progress=True` بده:

```python
import oxtapus as ox

df = ox.tsetmc.daily_prices(["فولاد", "خودرو"], progress=True)
```

اگه می‌خوای رویدادها رو خودت در رابط کاربری یا log پردازش کنی، یک callback بده:

```python
events = []
df = ox.tsetmc.daily_prices(["فولاد"], progress=events.append)
```

وقتی منبع `Content-Length` بده، درصد واقعی نمایش داده می‌شه و پایان دقیقاً ۱۰۰٪ است. اگر حجم
کل مشخص نباشه، Oxtapus درصد ساختگی تولید نمی‌کنه و فقط بایت و سرعت رو گزارش می‌ده. در دریافت
گروهی، تعداد موارد کامل‌شده، تلاش مجدد و خطا هم نمایش داده می‌شن.

</div>
