:py:mod:`oxtapus.econ`
======================

.. py:module:: oxtapus.econ


Submodules
----------
.. toctree::
   :titlesonly:
   :maxdepth: 1

   cbi/index.rst
   tgju/index.rst


Package Contents
----------------

Classes
~~~~~~~

.. autoapisummary::

   oxtapus.econ.TGJU




.. py:class:: TGJU


   دریافتِ داده‌هایِ گذشته‌یِ سایتِ www.tgiu.org

   .. py:method:: _get_hist_price(item)
      :staticmethod:


   .. py:method:: usd_irr()

      دریافتِ داده‌هایِ گذشته‌یِ دلار/ریال

      :rtype: pandas.DataFrame


   .. py:method:: sekke_emami()

      دریافتِ داده‌هایِ گذشته‌یِ سکه‌یِ امامی

      :rtype: pandas.DataFrame


   .. py:method:: nim_sekke()

      دریافتِ داده‌هایِ گذشته‌یِ نیم-سکه

      :rtype: pandas.DataFrame


   .. py:method:: rob_sekke()

      دریافتِ داده‌هایِ گذشته‌یِ ربعِ-سکه

      :rtype: pandas.DataFrame


   .. py:method:: ons()

      دریافتِ داده‌هایِ گذشته‌یِ اونس طلا

      :rtype: pandas.DataFrame



