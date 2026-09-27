<div dir="rtl" align="right" markdown="1">

# نصب

Oxtapus روی پایتون 3.11 تا 3.14 اجرا می‌شه. برای نصب نسخهٔ اصلی این دستور رو داخل ترمینال
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

</div>
