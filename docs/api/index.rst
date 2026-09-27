مرجع API پایتون
===============

.. raw:: html

   <div class="rtl-doc" dir="rtl">

این صفحه نمای کلی اشیاء، توابع و متدهای عمومی Oxtapus رو می‌ده. API ساده زیر دو منبع
``oxtapus.tsetmc`` و ``oxtapus.tgju`` قرار داره؛ ``Client`` و ``AsyncClient`` هم در صفحه‌های
جدا با تمام متدها مستند شدن.

TGJU
----

قیمت روزانه ارز و سکه
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autosummary::

   oxtapus.tgju.daily_prices

TSETMC
------

قیمت و دیده‌بان بازار
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autosummary::

   oxtapus.tsetmc.daily_prices
   oxtapus.tsetmc.market_watch
   oxtapus.tsetmc.quote
   oxtapus.tsetmc.market_depth
   oxtapus.tsetmc.investor_activity

جست‌وجو و اطلاعات ابزار
~~~~~~~~~~~~~~~~~~~~~~~

.. autosummary::

   oxtapus.tsetmc.instrument_search
   oxtapus.tsetmc.instrument_info
   oxtapus.tsetmc.instrument_identity

اختیار معامله و راهبری شرکتی
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autosummary::

   oxtapus.tsetmc.board_members
   oxtapus.tsetmc.option_chain

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

* :doc:`shortcuts` — تابع‌های منبع‌محوری که مستقیم دیتافریم می‌دن.
* :doc:`sync-client` — کلاینت همگام و فضای نام بازار، ابزار، دارایی و راهبری شرکتی.
* :doc:`async-client` — نسخهٔ ناهمگام با قابلیت‌های معادل.
* :doc:`results-settings` — ``FetchResult``، تبدیل خروجی و تنظیمات.
* :doc:`exceptions` — سلسله‌مراتب خطاهای تایپ‌شده.

.. raw:: html

   </div>

.. toctree::
   :hidden:
   :maxdepth: 2

   shortcuts
   sync-client
   async-client
   results-settings
   exceptions
