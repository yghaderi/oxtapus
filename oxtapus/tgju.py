import polars as pl
import requests


class TGJU:
    """
    .. raw:: html

        <div dir="rtl">
              داده‌هایِ گذشته‌یِ سایتِ tgju.org رو بهت می‌ده.
        </div>
    """

    def __init__(self, base_url: str = "https://api.tgju.org/v1"):
        self.base_url = base_url

    def _get_hist_price(self, item):
        url = f"{self.base_url}/market/indicator/summary-table-data/{item}"
        r = requests.get(url=url, timeout=(2, 6)).json()
        cols = ["open", "low", "high", "close", "_", "__", "date", "jdate"]
        df = pl.from_records(r["data"], schema=cols, orient="row")
        df = df.with_columns(
            date=pl.col("date").str.to_date(),
            jdate=pl.col("jdate").str.replace_all("/", "-"),
            open=pl.col("open").str.replace_all(",", "").cast(pl.Float64),
            high=pl.col("high").str.replace_all(",", "").cast(pl.Float64),
            low=pl.col("low").str.replace_all(",", "").cast(pl.Float64),
            close=pl.col("close").str.replace_all(",", "").cast(pl.Float64),
        ).select(["date", "jdate", "open", "high", "low", "close"])
        return df

    def usd_irr(self):
        """
        .. raw:: html

            <div dir="rtl">
             داده‌هایِ گذشته‌یِ دلار/ریال رو بهت می‌ده.
            </div>

        Returns
        -------
        pandas.DataFrame

        example
        ------
        >>> from oxtapus import TGJU
        >>> tgju = TGJU()
        >>> tgju.usd_irr()
        shape: (3_688, 6)
        ┌────────────┬────────────┬──────────┬──────────┬──────────┬──────────┐
        │ date       ┆ jdate      ┆ open     ┆ high     ┆ low      ┆ close    │
        │ ---        ┆ ---        ┆ ---      ┆ ---      ┆ ---      ┆ ---      │
        │ date       ┆ str        ┆ f64      ┆ f64      ┆ f64      ┆ f64      │
        ╞════════════╪════════════╪══════════╪══════════╪══════════╪══════════╡
        │ 2023-11-01 ┆ 1402-08-10 ┆ 514870.0 ┆ 517900.0 ┆ 513380.0 ┆ 516830.0 │
        │ 2023-10-31 ┆ 1402-08-09 ┆ 516770.0 ┆ 518060.0 ┆ 515370.0 ┆ 516600.0 │
        │ 2023-10-30 ┆ 1402-08-08 ┆ 511950.0 ┆ 514600.0 ┆ 510650.0 ┆ 514500.0 │
        │ 2023-10-29 ┆ 1402-08-07 ┆ 519550.0 ┆ 519560.0 ┆ 513350.0 ┆ 513560.0 │
        │ …          ┆ …          ┆ …        ┆ …        ┆ …        ┆ …        │
        │ 2011-11-29 ┆ 1390-09-08 ┆ 13400.0  ┆ 13400.0  ┆ 13400.0  ┆ 13400.0  │
        │ 2011-11-28 ┆ 1390-09-07 ┆ 13350.0  ┆ 13350.0  ┆ 13350.0  ┆ 13350.0  │
        │ 2011-11-27 ┆ 1390-09-06 ┆ 13440.0  ┆ 13440.0  ┆ 13440.0  ┆ 13440.0  │
        │ 2011-11-26 ┆ 1390-09-05 ┆ 13700.0  ┆ 13700.0  ┆ 13700.0  ┆ 13700.0  │
        └────────────┴────────────┴──────────┴──────────┴──────────┴──────────┘
        """
        return self._get_hist_price("price_dollar_rl")

    def sekke_emami(self):
        """
        .. raw:: html

            <div dir="rtl">
             داده‌هایِ گذشته‌یِ سکه‌یِ امامی رو بهت می‌ده.
            </div>

        Returns
        -------
        pandas.DataFrame

        example
        ------
        >>> from oxtapus import TGJU
        >>> tgju = TGJU()
        >>> tgju.sekke_emami().head(3)
        shape: (3, 6)
        ┌────────────┬────────────┬──────────┬──────────┬─────────┬──────────┐
        │ date       ┆ jdate      ┆ open     ┆ high     ┆ low     ┆ close    │
        │ ---        ┆ ---        ┆ ---      ┆ ---      ┆ ---     ┆ ---      │
        │ date       ┆ str        ┆ f64      ┆ f64      ┆ f64     ┆ f64      │
        ╞════════════╪════════════╪══════════╪══════════╪═════════╪══════════╡
        │ 2023-11-01 ┆ 1402-08-10 ┆ 2.9351e8 ┆ 2.9901e8 ┆ 2.925e7 ┆ 2.9601e8 │
        │ 2023-10-31 ┆ 1402-08-09 ┆ 2.9301e8 ┆ 2.9701e8 ┆ 2.923e8 ┆ 2.9701e8 │
        │ 2023-10-30 ┆ 1402-08-08 ┆ 2.9201e8 ┆ 2.9201e8 ┆ 2.903e8 ┆ 2.9133e8 │
        └────────────┴────────────┴──────────┴──────────┴─────────┴──────────┘
        """
        return self._get_hist_price("sekee")

    def nim_sekke(self):
        """
        .. raw:: html

            <div dir="rtl">
             داده‌هایِ گذشته‌یِ نیم-سکه رو بهت می‌ده.
            </div>

        Returns
        -------
        pandas.DataFrame
        """
        return self._get_hist_price("nim")

    def rob_sekke(self):
        """
        .. raw:: html

            <div dir="rtl">
             داده‌هایِ گذشته‌یِ ربعِ-سکه رو بهت می‌ده.
            </div>

        Returns
        -------
        pandas.DataFrame
        """
        return self._get_hist_price("rob")

    def ons(self):
        """
        .. raw:: html

            <div dir="rtl">
             داده‌هایِ گذشته‌یِ اونسِ طلا رو بهت می‌ده.
            </div>

        Returns
        -------
        pandas.DataFrame
        """
        return self._get_hist_price("ons")

    def silver(self):
        """
        .. raw:: html

            <div dir="rtl">
             داده‌هایِ گذشته‌یِ اونسِ نقره رو بهت می‌ده.
            </div>

        Returns
        -------
        pandas.DataFrame
        """
        return self._get_hist_price("silver")
