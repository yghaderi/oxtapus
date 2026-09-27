API منبع‌محور
============================

.. raw:: html

   <div class="rtl-doc" dir="rtl">

این توابع برای نوت‌بوک و تحلیل سریع مناسبن و مستقیماً ``polars.DataFrame`` برمی‌گردونن. نام
منبع همیشه در مسیر فراخوانی مشخصه. برای فرادادهٔ کامل از متدهای ``fetch_...`` کلاینت استفاده
کن.

TGJU: ارز و سکه
---------------

.. autofunction:: oxtapus.tgju.daily_prices

.. code-block:: pycon

   >>> import oxtapus as ox
   >>> frame = ox.tgju.daily_prices("سکه امامی", start="1403/10/12")
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

TSETMC: قیمت و بازار
------------------------

.. autofunction:: oxtapus.tsetmc.daily_prices

.. autofunction:: oxtapus.tsetmc.market_watch

.. autofunction:: oxtapus.tsetmc.quote

.. autofunction:: oxtapus.tsetmc.market_depth

.. autofunction:: oxtapus.tsetmc.investor_activity

.. code-block:: pycon

   >>> quote = ox.tsetmc.quote("فولاد")
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

.. autofunction:: oxtapus.tsetmc.instrument_search

.. autofunction:: oxtapus.tsetmc.instrument_info

.. autofunction:: oxtapus.tsetmc.instrument_identity

.. autofunction:: oxtapus.tsetmc.board_members

.. autofunction:: oxtapus.tsetmc.option_chain

.. raw:: html

   </div>
