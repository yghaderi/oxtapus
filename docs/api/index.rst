مرجع API پایتون
===============

.. raw:: html

   <div class="rtl-doc" dir="rtl">

این صفحه نمای کلی آبجکت‌ها، توابع و متدهای عمومی Oxtapus رو می‌ده. اسم‌های موجود در
``oxtapus.__all__`` سطح اصلی API هستن؛ namespaceهای ``Client`` و ``AsyncClient`` هم در
صفحه‌های جدا با تمام متدها مستند شدن.

میان‌برهای دیتافریم
-------------------

.. autosummary::

   oxtapus.asset_history
   oxtapus.daily_prices
   oxtapus.market_watch
   oxtapus.quote
   oxtapus.market_depth
   oxtapus.investor_activity
   oxtapus.instrument_search
   oxtapus.instrument_info
   oxtapus.instrument_identity
   oxtapus.board_members
   oxtapus.option_chain

کلاینت‌ها
---------

.. autosummary::

   oxtapus.Client
   oxtapus.AsyncClient

نتیجه و تنظیمات
---------------

.. autosummary::

   oxtapus.FetchResult
   oxtapus.Settings
   oxtapus.DataLayer

صفحه‌های جزئیات
---------------

* :doc:`shortcuts` — تابع‌های ساده‌ای که مستقیم دیتافریم می‌دن.
* :doc:`sync-client` — کلاینت همگام و namespaceهای بازار، ابزار، دارایی و راهبری شرکتی.
* :doc:`async-client` — نسخهٔ async با قابلیت‌های معادل.
* :doc:`results-settings` — ``FetchResult``، تبدیل خروجی و تنظیمات.
* :doc:`exceptions` — سلسله‌مراتب خطاهای تایپ‌شده.

.. raw:: html

   </div>
