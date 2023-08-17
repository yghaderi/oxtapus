from urllib.parse import urlencode
import pandas as pd
from ..utils import get
from .tsetmc_utils import cols, URL, ced


class TSETMC:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.url = URL()

    def market_watch(self, **kwargs):
        main = get(self.url.mw(**kwargs)).json()["marketwatch"]
        df = pd.json_normalize(
            main, "blDs", list(cols.mw.rename.keys()), record_prefix="ob_"
        )
        return ced.mw(df)

    def option_market_watch(self):
        # option df
        option = self.market_watch(option=True).drop(cols.omw.drop, axis=1)
        # underlying asset
        ua = self.market_watch(stock=True, etf=True).drop(cols.omw.drop, axis=1)
        ua = ua[(ua["ins_id"].str.endswith("1"))].add_prefix("ua_")
        ua = ua[ua.ua_quote.astype(int) == 1]
        ua.drop_duplicates(inplace=True)
        ua.drop(["ua_name_far"], axis=1, inplace=True)
        # marge option with ua df and clean and extend data
        df = ced.omw(option=option, ua=ua)
        return df.rename(columns=cols.omw.rename)

    def search_instrument_code(self, symbol_far: str):
        data = get(self.url.search_ins_code(symbol_far)).json()["instrumentSearch"]
        for i in data:
            try:
                if (
                    ced.arabic_char(i["lVal18AFC"]) == ced.arabic_char(symbol_far)
                ) and (i["lastDate"] == 1):
                    return i["insCode"]
            except:
                print(f"Please enter the valid symbol! '{symbol_far}'")

    def instrument_info(self, ins_codes: list):
        """
        take instrument info
        :param ins_codes: list of instrument code
        :return: pandas data-frame
        """
        ins_info = []
        for ins_code in ins_codes:
            ins_info.append(
                ced.ins_info(get(self.url.ins_info(ins_code)).json()["instrumentInfo"])
            )
        return pd.DataFrame.from_records(ins_info)

    def option_info(self):
        return self.instrument_info(self.market_watch(option=True)["ins_code"].values)[
            cols.option_info.rep
        ].rename(columns={"symbol": "ua"})

    def stock_info(self):
        return self.instrument_info(self.market_watch(stock=True)["ins_code"].values)

    def etf_info(self):
        return self.instrument_info(self.market_watch(etf=True)["ins_code"].values)

    def bond_info(self):
        return self.instrument_info(self.market_watch(bond=True)["ins_code"].values)

    def hist_price(self, symbol_far="فولاد", ins_code=None):
        """
        take adjusted price history.
        :param ins_code: int or str, instrument code.
        :param symbol_far: str , instrument symbol
        :return: pandas data-frame
        """
        if not ins_code:
            ins_code = self.search_instrument_code(symbol_far)

        main = get(self.url.hist_price(ins_code)).json()["closingPriceDaily"]
        df = pd.DataFrame(main).rename(columns=cols.hist_price.rename)
        return ced.date(df)

    def adj_hist_price(self, symbol_far="فولاد", ins_code=None):
        """
        take adjusted price history.
        :param ins_code: int or str, instrument code.
        :param symbol_far: str , instrument symbol
        :return: pandas data-frame
        """
        if not ins_code:
            ins_code = self.search_instrument_code(symbol_far)
        return ced.adj_price(self.hist_price(ins_code))

    def client_type(self, ins_code):
        """
        take Individual and Institutional trade data
        :param ins_code: int or str, instrument code.
        :return: pandas data-frame
        """

        main = get(self.url.client_type(ins_code)).json()["clientType"]
        df = pd.DataFrame(main)
        df = df.rename(columns=cols.client_type.rename)[cols.client_type.rep]
        return ced.date(df).applymap(int)

    @staticmethod
    def share_change(ins_code):
        url = (
            f"http://cdn.tsetmc.com/api/Instrument/GetInstrumentShareChange/{ins_code}"
        )
