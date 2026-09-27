مستندات Oxtapus
================

.. raw:: html

   <div class="rtl-doc" dir="rtl">

Oxtapus یک SDK تایپ‌شده و مبتنی بر Polars برای داده‌های بازار مالی ایرانه. داده‌های ابزارهای
بورس تهران از TSETMC و تاریخچهٔ ارز و سکه از TGJU به‌شکل ``polars.DataFrame`` برمی‌گردن.

مسیر معمول استفاده از :doc:`getting-started/installation` و
:doc:`getting-started/quickstart` شروع می‌شه. :doc:`api/index` فهرست کامل توابع و متدهای
عمومی رو با امضا، ورودی، خروجی، مثال قابل‌کپی و نمونهٔ خروجی ارائه می‌کنه.

یک نمونهٔ کوتاه
----------------

.. code-block:: pycon

   >>> import oxtapus as ox
   >>> usd = ox.asset_history("دلار", start="۱۴۰۳/۱۰/۱۲")
   >>> usd.select("trading_date", "close_price").tail(3)
   shape: (3, 2)
   ┌──────────────┬─────────────┐
   │ trading_date ┆ close_price │
   │ ---          ┆ ---         │
   │ date         ┆ i64         │
   ╞══════════════╪═════════════╡
   │ …            ┆ …           │
   └──────────────┴─────────────┘

.. note::

   مقدارهای نمونه کوتاه شده‌ان؛ تعداد ردیف و قیمت واقعی به زمان دریافت و بازهٔ انتخابی بستگی
   داره.

.. raw:: html

   </div>

.. toctree::
   :maxdepth: 2
   :caption: شروع کار

   getting-started/installation
   getting-started/quickstart
   getting-started/jupyter
   getting-started/financial-modeling

.. toctree::
   :maxdepth: 2
   :caption: مرجع API پایتون

   api/index
   api/shortcuts
   api/sync-client
   api/async-client
   api/results-settings
   api/exceptions

.. toctree::
   :maxdepth: 2
   :caption: راهنماها

   guides/sync-client
   guides/async-client
   guides/progress
   guides/retries
   guides/batch-downloads
   guides/incremental-ingestion
   guides/storage
   guides/observability

.. toctree::
   :maxdepth: 2
   :caption: مرجع داده

   reference/datasets
   reference/data-dictionary
   reference/naming-conventions
   reference/tsetmc-endpoints
   reference/tgju-assets
   reference/dates
   reference/configuration
   reference/exceptions
   troubleshooting

.. toctree::
   :maxdepth: 2
   :caption: Architecture and development (English)

   concepts/architecture
   concepts/providers
   concepts/data-layers
   concepts/schema-versioning
   concepts/instrument-identifiers
   development/architecture-rules
   development/provider-development
   development/testing
   development/current-state-audit
   development/reference-architecture-review
   development/tsetmc-api-inventory
   decisions/index
   decisions/0001-httpx2-transport
   decisions/0002-native-sync-async
   decisions/0003-provider-fetcher
   decisions/0004-medallion
   decisions/0005-canonical-naming
   decisions/0006-storage
   decisions/0007-schema-versioning
   decisions/0008-hard-api-replacement
   decisions/0010-endpoint-verification
   decisions/0011-progress-events
