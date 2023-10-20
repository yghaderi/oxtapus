import pandas as pd
from oxtapus.utils import get


class TGJU:
    """
    دریافتِ داده‌هایِ گذشته‌یِ سایتِ www.tgju.org
    """

    def __init__(self):
        pass

    @staticmethod
    def _get_hist_price(item):
        url = f"https://api.tgju.org/v1/market/indicator/summary-table-data/{item}"
        main = get(url=url, timeout=(2, 6), verify=True).json()
        df = pd.DataFrame().from_records(main["data"]).drop([4, 5], axis=1)
        df.columns = ["open", "low", "high", "close", "date", "jdate"]
        df[["open", "low", "high", "close"]] = df[
            ["open", "low", "high", "close"]
        ].applymap(lambda x: float(x.replace(",", "")))
        df["date"] = pd.to_datetime(df.date)
        return df.set_index("date").sort_index()

    def usd_irr(self):
        """
        دریافتِ داده‌هایِ گذشته‌یِ دلار/ریال

        Returns
        -------
        pandas.DataFrame
        """
        return self._get_hist_price("price_dollar_rl")

    def sekke_emami(self):
        """
        دریافتِ داده‌هایِ گذشته‌یِ سکه‌یِ امامی

        Returns
        -------
        pandas.DataFrame
        """
        return self._get_hist_price("sekee")

    def nim_sekke(self):
        """
        دریافتِ داده‌هایِ گذشته‌یِ نیم-سکه

        Returns
        -------
        pandas.DataFrame
        """
        return self._get_hist_price("nim")

    def rob_sekke(self):
        """
        دریافتِ داده‌هایِ گذشته‌یِ ربعِ-سکه

        Returns
        -------
        pandas.DataFrame
        """
        return self._get_hist_price("rob")

    def ons(self):
        """
        دریافتِ داده‌هایِ گذشته‌یِ اونس طلا

        Returns
        -------
        pandas.DataFrame
        """
        return self._get_hist_price("ons")
