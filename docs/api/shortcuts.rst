میان‌برهای دیتافریم
============================

.. raw:: html

   <div class="rtl-doc" dir="rtl">

این توابع برای نوت‌بوک و تحلیل سریع مناسبن و مستقیماً ``polars.DataFrame`` برمی‌گردونن. برای
metadata کامل از متدهای ``fetch_...`` کلاینت استفاده کن.

ارز و سکه
---------

.. autofunction:: oxtapus.asset_history

.. code-block:: pycon

   >>> import oxtapus as ox
   >>> frame = ox.asset_history("سکه امامی", start="۱۴۰۳/۱۰/۱۲")
   >>> frame.select("asset_code", "trading_date", "close_price").tail(2)
   shape: (2, 3)
   ┌─────────────────┬──────────────┬─────────────┐
   │ asset_code      ┆ trading_date ┆ close_price │
   │ ---             ┆ ---          ┆ ---         │
   │ str             ┆ date         ┆ i64         │
   ╞═════════════════╪══════════════╪═════════════╡
   │ emami_gold_coin ┆ …            ┆ …           │
   │ emami_gold_coin ┆ …            ┆ …           │
   └─────────────────┴──────────────┴─────────────┘

قیمت و بازار
------------

.. autofunction:: oxtapus.daily_prices

.. autofunction:: oxtapus.market_watch

.. autofunction:: oxtapus.quote

.. autofunction:: oxtapus.market_depth

.. autofunction:: oxtapus.investor_activity

.. code-block:: pycon

   >>> quote = ox.quote("فولاد")
   >>> quote.select("symbol", "last_price", "close_price")
   shape: (1, 3)
   ┌────────┬────────────┬─────────────┐
   │ symbol ┆ last_price ┆ close_price │
   │ ---    ┆ ---        ┆ ---         │
   │ str    ┆ i64        ┆ i64         │
   ╞════════╪════════════╪═════════════╡
   │ فولاد  ┆ …          ┆ …           │
   └────────┴────────────┴─────────────┘

اطلاعات ابزار و شرکت
--------------------

.. autofunction:: oxtapus.instrument_search

.. autofunction:: oxtapus.instrument_info

.. autofunction:: oxtapus.instrument_identity

.. autofunction:: oxtapus.board_members

.. autofunction:: oxtapus.option_chain

.. raw:: html

   </div>
