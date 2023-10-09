:py:mod:`oxtapus.ise`
=====================

.. py:module:: oxtapus.ise


Submodules
----------
.. toctree::
   :titlesonly:
   :maxdepth: 1

   codal/index.rst
   rahavard/index.rst
   tsetmc/index.rst


Package Contents
----------------

Classes
~~~~~~~

.. autoapisummary::

   oxtapus.ise.TSETMC
   oxtapus.ise.Rahavard
   oxtapus.ise.Codal




.. py:class:: TSETMC(**kwargs)


   .. py:method:: market_watch(**kwargs)


   .. py:method:: option_market_watch()

      get option market-watch
      :return: pandas.DataFrame


   .. py:method:: search_instrument_code(symbol_far: str)

      get instrument code by search symbol-far
      :return:string


   .. py:method:: instrument_info(ins_code: list)

      get instrument info
      :param ins_code: list of instrument code
      :return: pandas data-frame


   .. py:method:: option_info_comp(ins_id: list)

      get complimentary option info.
      :param ins_id: list, instrument id
      :return: pandas.DataFrame


   .. py:method:: option_info()

      get option base info
      :return:pandas.DataFrame


   .. py:method:: stock_info()


   .. py:method:: etf_info()


   .. py:method:: bond_info()


   .. py:method:: handle_args()


   .. py:method:: hist_price(symbol_far='فولاد', ins_code=None)

      take adjusted price history.
      :param ins_code: int or str, instrument code.
      :param symbol_far: str , instrument symbol
      :return: pandas data-frame


   .. py:method:: adj_hist_price(symbol_far='فولاد', ins_code=None)

      take adjusted price history.
      :param ins_code: int or str, instrument code.
      :param symbol_far: str , instrument symbol
      :return: pandas data-frame


   .. py:method:: client_type(ins_code)

      take Individual and Institutional trade data
      :param ins_code: int or str, instrument code.
      :return: pandas data-frame


   .. py:method:: share_change(symbol_far='فولاد', ins_code=None)

      Get share change history.
      :param ins_code: int or str, instrument code.
      :param symbol_far: str , instrument symbol
      :return: pandas data-frame


   .. py:method:: all_index()

      Get the latest data of all index
      :return pandas data-frame


   .. py:method:: index_ticker_symbols(index_code)

      Get associated symbols that track by index
      :param index_code: int or str
      :return pandas data-frame


   .. py:method:: index_hist(index_code)


   .. py:method:: last_ins_info(symbol_far='فولاد', ins_code=None)


   .. py:method:: intraday_trades(symbol_far='فولاد', ins_code=None)

      Get intraday instrument trade


   .. py:method:: intraday_trades_base_timeframe(symbol_far='فولاد', ins_code=None, timeframe: str = '5T') -> pandas.DataFrame

      Get intraday instrument trade base on time-frame
      :param timeframe: str like 5T -> 5 minute, 30S -> 30 second , ...


   .. py:method:: get_last_market_activity_datetime()



.. py:class:: Rahavard


   .. py:method:: stock()


   .. py:method:: symbol_id()


   .. py:method:: balance_sheet(symbol_far)


   .. py:method:: income_statements(symbol_far)


   .. py:method:: cash_flow(symbol_far)



.. py:class:: Codal(**kwargs)


   Bases: :py:obj:`oxtapus.ise.codal_utils.URL`

   .. py:method:: letters()


   .. py:method:: income_statements()


   .. py:method:: balance_sheet()



