import asyncio
import pandas as pd
from ..utils import get, async_get
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
        """get option market-watch
        :return: pandas.DataFrame
        """
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
        """get instrument code by search symbol-far
        :return:string
        """
        data = get(self.url.search_ins_code(symbol_far)).json()["instrumentSearch"]
        for i in data:
            try:
                if (
                    ced.arabic_char(i["lVal18AFC"]) == ced.arabic_char(symbol_far)
                ) and (i["lastDate"] == 1):
                    return i["insCode"]
            except:
                print(f"Please enter the valid symbol! '{symbol_far}'")

    def instrument_info(self, ins_code: list):
        """get instrument info
        :param ins_code: list of instrument code
        :return: pandas data-frame
        """

        task = [async_get(url=self.url.ins_info(i)) for i in ins_code]

        async def main():
            return await asyncio.gather(*task)

        loop = asyncio.get_event_loop()
        ins_info_ = loop.run_until_complete(main())
        ins_info = []
        for i in ins_info_:
            try:
                ins_info.append(ced.ins_info(i.get("instrumentInfo")))
            except AttributeError as e:
                print(e)

        df = pd.DataFrame.from_records(ins_info)
        return df

    def option_info_comp(self, ins_id: list):
        """get complimentary option info.
        :param ins_id: list, instrument id
        :return: pandas.DataFrame
        """
        task = [async_get(url=self.url.option_info_comp(i)) for i in ins_id]

        async def main():
            return await asyncio.gather(*task)

        loop = asyncio.get_event_loop()
        ins_info_ = loop.run_until_complete(main())
        ins_info = []
        for i in ins_info_:
            try:
                ins_info.append(i.get("instrumentOption"))
            except AttributeError as e:
                print(e)
        df = pd.DataFrame(ins_info).rename(columns=cols.option_info_comp.rename)[
            cols.option_info_comp.rep
        ]
        return df

    def option_info(self):
        """get option base info
        :return:pandas.DataFrame
        """
        option_mw = self.market_watch(option=True)
        df = self.instrument_info(option_mw["ins_code"].unique())[
            cols.option_info.rep
        ].rename(columns={"symbol": "ua"})
        df_comp = self.option_info_comp(option_mw["ins_id"].unique())
        return df.merge(df_comp, on="ins_code", how="inner")

    def stock_info(self):
        return self.instrument_info(self.market_watch(stock=True)["ins_code"].unique())

    def etf_info(self):
        return self.instrument_info(self.market_watch(etf=True)["ins_code"].unique())

    def bond_info(self):
        return self.instrument_info(self.market_watch(bond=True)["ins_code"].unique())

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
