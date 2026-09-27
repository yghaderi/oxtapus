کلاینت ناهمگام
==============

.. raw:: html

   <div class="rtl-doc" dir="rtl">

``AsyncClient`` همتای ناهمگام کلاینت همگامه. Oxtapus حلقهٔ رویداد (``event loop``) رو نمی‌سازه
و کنترل نمی‌کنه؛ متدها رو داخل حلقهٔ رویداد برنامه یا با ``await`` مستقیم Jupyter صدا بزن.

.. code-block:: pycon

   >>> from oxtapus import AsyncClient
   >>> async with AsyncClient() as client:
   ...     usd = await client.assets.history("دلار")

.. raw:: html

   </div>

AsyncClient
-----------

.. autoclass:: oxtapus.api.async_client.AsyncClient
   :members:
   :member-order: bysource
   :show-inheritance:

AsyncMarketNamespace
--------------------

.. autoclass:: oxtapus.api.async_client.AsyncMarketNamespace
   :members:
   :member-order: bysource

AsyncInstrumentNamespace
------------------------

.. autoclass:: oxtapus.api.async_client.AsyncInstrumentNamespace
   :members:
   :member-order: bysource

AsyncAssetNamespace
-------------------

.. autoclass:: oxtapus.api.async_client.AsyncAssetNamespace
   :members:
   :member-order: bysource

AsyncGovernanceNamespace
------------------------

.. autoclass:: oxtapus.api.async_client.AsyncGovernanceNamespace
   :members:
   :member-order: bysource
