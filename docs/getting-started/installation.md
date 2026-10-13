<div dir="rtl" align="right" markdown="1">

# نصب

Oxtapus روی پایتون 3.11 تا 3.15 اجرا می‌شه. برای نصب نسخهٔ اصلی این دستور رو داخل ترمینال
بزن:

```bash
python -m pip install oxtapus
```

اگه داخل Jupyter هستی، اول خط علامت `%` بذار و بعد از نصب kernel رو یک‌بار restart کن:

```python
%pip install oxtapus
```

نسخهٔ اصلی همه‌چیز لازم برای دریافت داده و ساخت `Polars DataFrame` رو داره. تبدیل به Pandas
یا Arrow، ذخیره در DuckDB و HTTP/2 اختیاریه:

```bash
python -m pip install 'oxtapus[arrow,pandas,duckdb,http2]'
```

برای مطمئن‌شدن از نصب، این دستور باید شماره نسخه رو چاپ کنه:

```bash
python -c "import oxtapus; print(oxtapus.__version__)"
```

اگه چند محیط پایتون داری، حتماً `pip` رو با همون `python` اجرا کن که قراره کدت رو اجرا کنه.

## نصب و ارتقا با uv

در پروژه‌ای که با `uv` مدیریت می‌شه، برای نصب نسخهٔ 1.3.0 یا جدیدتر این دستور رو بزن:

```bash
uv add 'oxtapus>=1.3.0'
```

برای ارتقای بستهٔ موجود و به‌روزکردن محیط پروژه:

```bash
uv sync --upgrade-package oxtapus
```

اگه از رابط `uv pip` برای یک محیط مجازی استفاده می‌کنی:

```bash
uv pip install --upgrade 'oxtapus>=1.3.0'
```

برای دیدن نسخه‌ای که واقعاً در محیط پروژه نصب شده:

```bash
uv run python -c "import oxtapus; print(oxtapus.__version__)"
```

ارتقا باید با محدودیت‌های `pyproject.toml` سازگار باشه. برای نصب یک نسخهٔ مشخص از دو علامت
مساوی استفاده کن؛ مثلاً `uv add 'oxtapus==1.3.0'`.

</div>
