import functools
import asyncio
import datetime
from typing import List
import pandas as pd

from ..utils import get, async_get
from .tsetmc_utils import cols, URL, ced


class TSETMC:
    """Get clean and fast all data from tsetmc.com."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.url = URL()

    def market_watch(self, stock: bool = False,
                     ifb_paye: bool = False,
                     mortgage: bool = False,
                     cum_right: bool = False,
                     bond: bool = False,
                     option: bool = False,
                     futures: bool = False,
                     etf: bool = False,
                     commodity: bool = False, ):
        """
        Get Market Watch data.

        Parameters
        ----------
        stock
            if True add stock data, default is False
        ifb_paye
            if True add ifb_pay data, default is False (فرابورس-پایه)
        mortgage
            if True add mortgage data, default is False
        cum_right
            if True add cum_right data, default is False
        bond
            if True add bond data, default is False
        option
            if True add option data, default is False
        futures
            if True add futures data, default is False
        etf
            if True add etf data, default is False
        commodity
            if True add commodity data, default is False

        Returns
        -------
        pandas.DataFrame
        """

        main = get(self.url.mw(stock,
                               ifb_paye,
                               mortgage,
                               cum_right,
                               bond,
                               option,
                               futures,
                               etf,
                               commodity)).json()["marketwatch"]
        df = pd.json_normalize(
            main, "blDs", list(cols.mw.rename.keys()), record_prefix="ob_"
        )
        return ced.mw(df)

    def option_market_watch(self):
        """
        Get Option Market Watch with extending and underling-asset data. That's all you need to model options.

        Returns
        -------
        pandas.DataFrame
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
        """
        Get instrument code by search symbol-far.

        Parameters
        ----------
        symbol_far
            farsi name of the symbol.
            نام فارسیِ نماد.

        Returns
        -------
        str
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

    def instrument_info(self, ins_code: List[str]):
        """
        Get instrument info.

        Parameters
        ----------
        ins_code
            list of instrument code

        Returns
        -------
        pandas.DataFrame
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

    def option_info_comp(self, ins_id: List[str]):
        """
        Get complimentary option info.

        Parameters
        ----------
        ins_id
            list of instrument id

        Returns
        -------
        pandas.DataFrame
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
        """Get option base info.

        Returns
        -------
        pandas.DataFrame
        """
        option_mw = self.market_watch(option=True)
        df = self.instrument_info(option_mw["ins_code"].unique())[
            cols.option_info.rep
        ].rename(columns={"symbol": "ua"})
        df_comp = self.option_info_comp(option_mw["ins_id"].unique())
        return df.merge(df_comp, on="ins_code", how="inner")

    def stock_info(self):
        """Get stock info.

        Returns
        -------
        pandas.DataFrame
        """
        return self.instrument_info(self.market_watch(stock=True)["ins_code"].unique())

    def etf_info(self):
        """Get ETFs info.

        Returns
        -------
        pandas.DataFrame
        """
        return self.instrument_info(self.market_watch(etf=True)["ins_code"].unique())

    def bond_info(self):
        """Get bonds info.

        Returns
        -------
        pandas.DataFrame
        """
        return self.instrument_info(self.market_watch(bond=True)["ins_code"].unique())

    def _handle_args(func):
        @functools.wraps(func)
        def wrapper(self, symbol_far="فولاد", ins_code=None, *args, **kwargs):
            if not ins_code:
                ins_code = self.search_instrument_code(symbol_far)
            return func(self, symbol_far, ins_code)

        return wrapper

    @_handle_args
    def hist_price(self, symbol_far: str | None = "فولاد", ins_code: str | None = None):
        """Get price history.

        .. warning::
             سرعتِ گرفتن داده با استفاده از **کدِ نماد** حدودن ۲ برابرِ **نماد** است

        .. note::
            یا **کدِ نماد** رو وارد کنید یا **نماد** رو

        Parameters
        ----------
        ins_code
            instrument code
        symbol_far
            instrument symbol

        Returns
        -------
        pandas.DataFrame
        """
        main = get(self.url.hist_price(ins_code)).json()["closingPriceDaily"]
        df = pd.DataFrame(main).rename(columns=cols.hist_price.rename)
        return ced.date(df)

    @_handle_args
    def adj_hist_price(self, symbol_far: str | None = "فولاد", ins_code: str | None = None):
        """Get adjusted price history.

        .. warning::
             سرعتِ گرفتن داده با استفاده از **کدِ نماد** حدودن ۲ برابرِ **نماد** است

        .. note::
            یا **کدِ نماد** رو وارد کنید یا **نماد** رو

        Parameters
        ----------
        ins_code
            instrument code
        symbol_far
            instrument symbol

        Returns
        -------
        pandas.DataFrame
        """
        return ced.adj_price(self.hist_price(ins_code))

    def client_type(self, ins_code: str):
        """
        Get Individual and Institutional (حقیقی-حقوقی) trade data.

        Parameters
        ----------
        ins_code
            instrument code

        Returns
        -------
        pandas.DataFrame
        """
        main = get(self.url.client_type(ins_code)).json()["clientType"]
        df = pd.DataFrame(main)
        df = df.rename(columns=cols.client_type.rename)[cols.client_type.rep]
        return ced.date(df).applymap(int)

    @_handle_args
    def share_change(self, symbol_far: str | None = "فولاد", ins_code: str | None = None):
        """
        Get share change history.

        .. warning::
             سرعتِ گرفتن داده با استفاده از **کدِ نماد** حدودن ۲ برابرِ **نماد** است

        .. note::
            یا **کدِ نماد** رو وارد کنید یا **نماد** رو

        Parameters
        ----------
        ins_code
            instrument code
        symbol_far
            instrument symbol

        Returns
        -------
        pandas.DataFrame
        """
        main = get(self.url.share_change(ins_code)).json().get("instrumentShareChange")
        df = pd.DataFrame(main).rename(columns=cols.share_change.rename)[
            cols.share_change.rep
        ]
        return ced.date(df)

    def all_index(self):
        """
        Get the latest data of all index.

        Returns
        -------
        pandas.DataFrame
        """
        main = get(self.url.all_index()).json()["indexB1"]
        return pd.DataFrame(main).rename(columns=cols.all_index.rename)[
            cols.all_index.rep
        ]

    def index_ticker_symbols(self, index_code):
        """
        Get associated symbols that track by index.

        Parameters
        ----------
        index_code
            index code

        Returns
        -------
        pandas.DataFrame
        """
        main = get(self.url.index_ticker_symbols(index_code)).json()["indexCompany"]
        return pd.DataFrame(ced.index_traker_symbols(index_code, main))

    def index_hist(self, index_code):
        """
        Get index history.

        Parameters
        ----------
        index_code
            index code

        Returns
        -------
        pandas.DataFrame
        """
        main = get((self.url.index_hist(index_code))).json()["indexB2"]
        df = pd.DataFrame(main).rename(columns=cols.index_hist.rename)
        return ced.date(df)

    @_handle_args
    def last_ins_info(self, symbol_far: str | None = "فولاد", ins_code: str | None = None):
        """
        Get last instrument info that show on main stock page.

        .. warning::
             سرعتِ گرفتن داده با استفاده از **کدِ نماد** حدودن ۲ برابرِ **نماد** است

        .. note::
            یا **کدِ نماد** رو وارد کنید یا **نماد** رو

        Parameters
        ----------
        ins_code
            instrument code
        symbol_far
            instrument symbol

        Returns
        -------
        pandas.DataFrame
        """
        main = get(url=self.url.last_ins_info(ins_code)).json()["closingPriceInfo"]
        df = pd.DataFrame([ced.last_ins_info(main)]).rename(
            columns=cols.last_ins_info.rename
        )[cols.last_ins_info.rep]
        return df

    @_handle_args
    def intraday_trades(self, symbol_far: str | None = "فولاد", ins_code: str | None = None):
        """
        Get intraday instrument trade.

        .. warning::
             سرعتِ گرفتن داده با استفاده از **کدِ نماد** حدودن ۲ برابرِ **نماد** است

        .. note::
            یا **کدِ نماد** رو وارد کنید یا **نماد** رو

        Parameters
        ----------
        ins_code
            instrument code
        symbol_far
            instrument symbol

        Returns
        -------
        pandas.DataFrame
        """
        main = get(url=self.url.intraday_trades(ins_code)).json()["trade"]
        date = get(url=self.url.last_ins_info(ins_code)).json()["closingPriceInfo"][
            "finalLastDate"
        ]
        df = pd.DataFrame(main).rename(columns=cols.intraday_trades.rename)
        df = df.assign(
            datetime=df.time.apply(
                lambda x: datetime.datetime.strptime(f"{date} {x}", "%Y%m%d %H%M%S")
            )
        )
        return df[cols.intraday_trades.rep]

    def intraday_trades_base_timeframe(
            self, symbol_far: str | None = "فولاد", ins_code: str | None = None, timeframe: str = "5T"
    ) -> pd.DataFrame:
        """
        Get intraday instrument trade base on time-frame.

        .. warning::
             سرعتِ گرفتن داده با استفاده از **کدِ نماد** حدودن ۲ برابرِ **نماد** است

        .. note::
            یا **کدِ نماد** رو وارد کنید یا **نماد** رو

        Parameters
        ----------
        ins_code
            instrument code
        symbol_far
            instrument symbol
        timeframe
            like 5T -> 5 minute, 30S -> 30 second

        Returns
        -------
        pandas.DataFrame
        """
        df = self.intraday_trades(symbol_far=symbol_far, ins_code=ins_code).set_index(
            "datetime"
        )
        df = df.resample(timeframe.upper()).agg(
            {"price": ["first", "min", "max", "last"], "volume": "sum"}
        )
        df.columns = ["open", "low", "high", "close", "volume"]
        return df

    def get_last_market_activity_datetime(self):
        """
        Get last market activity datetime.

        Returns
        -------
        datetime.datetime
        """
        main = get(self.url.last_market_activity()).json().get("marketOverview")
        date = main.get("marketActivityDEven")
        time = main.get("marketActivityHEven")
        return datetime.datetime.strptime(f"{date} {time}", "%Y%m%d %H%M%S")
