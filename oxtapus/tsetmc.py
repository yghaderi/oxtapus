import functools
from dataclasses import dataclass
import polars as pl

from oxtapus.utils.http import requests, async_requests
from oxtapus.utils import json_normalize, word_normalize, manipulation_cols
from oxtapus.utils.tsetmc import URL, cols


@dataclass
class InsCode:
    ins_code: int | list[int] | str | list[str] | None


@dataclass
class Symbol:
    symbol: str | list[str] | None


class TSETMC:
    def __init__(self, async_req):
        self._requests = async_requests if async_req else requests
        self.url = URL()

    @property
    def requests(self):
        return self._requests

    @requests.setter
    def requests(self, async_req):
        if async_req:
            self._requests = async_requests
        else:
            self._requests = requests

    def mw(self, sections: list[str]):
        """
        .. raw:: html

            <div dir="rtl">
                مارکت-واچ رو بر اساسِ بخش‌هایی که می‌خواین استخراج می‌کنه و تمیز شده بهتون می‌ده.
            </div>

        Parameters
        ----------
        sections: list[str]
            - stock: سهام
            - ifb_paye: پایه‌یِ-فرابورس
            - mortgage: اوراقِ مسکن
            - cum_right: حقِ-تقدم
            - bond: اوراقِ بدهی
            - options: اختیارِ معامله
            - futures: آتی
            - etf: صندوق‌هایِ قابلِ-معامله
            - commodity: کالا

        Returns
        -------
        polars.DataFrame

        example
        -------
        >>> from oxtapus import TSETMC
        >>> tsetmc = TSETMC()
        >>> tsetmc.mw(["stock", "etf", "options"])
        """
        r = self.requests(self.url.mw(sections), response="json").get("marketwatch")
        df = pl.from_dicts(json_normalize(r, "blDs", "ob_"), schema_overrides={"pe": pl.Utf8})
        df = manipulation_cols(df, cols=cols.mw_orderbook)
        df = manipulation_cols(df, cols=cols.mw)
        return df

    def options_mw(self):
        """
        .. raw:: html

            <div dir="rtl">
                داده‌هایِ صفحه‌یِ مارکت-واچِ مربوط به اخیتارِ-معامله و داراییِ پایه رو استخراج و چند
                مشخصه‌یِ دیگه که برایِ مدل-سازی‌های اختیارِ-معالمه نیاز است رو  اضافه می‌کنه.
            </div>

        .. note::
            .. raw:: html

                <div dir="rtl">
                    خرجی در کمتر از ۱ ثانیه داده می‌شه. پس اگه بیشتر زمان ببره، احتمالن ی چیزِ دیگه‌ای درست نیست!
                </div>


        Returns
        -------
        option-market-watch: polars.DataFrame

        example
        -------
        >>> from oxtapus import TSETMC
        >>> tsetmc = TSETMC()
        >>> tsetmc.options_mw()
        """
        o_df = manipulation_cols(self.mw(["options"]), cols=cols.options_mw).with_columns(
            pl.col("ins_id").str.slice(4, length=4).alias("key")
        )
        ua_df = (manipulation_cols(self.mw(["stock", "etf"]), cols=cols.options_ua_mw)
                 .filter(pl.col("ua_ob_level") == 1)
                 .with_columns(pl.col("ua_ins_id").str.slice(4, length=4).alias("key")))
        return o_df.join(ua_df, on="key", how="inner")

    def search_ins_code(self, symbol: str):
        """
        .. raw:: html

            <div dir="rtl">
                کدِ صفحه‌ی نماد/ابزارِ-معاملاتی رو استخراج می‌کنه.
            </div>

        Parameters
        ----------
        symbol: str
            نماد

        Returns
        -------
        isn-code: str

        example
        -------
        >>> from oxtapus import TSETMC
        >>> tsetmc = TSETMC()
        >>> tsetmc.search_ins_code("شپدیس")
        '20562694899904339'
        """
        r = self.requests(self.url.search_ins_code(symbol))["instrumentSearch"]
        for i in r:
            if (
                    word_normalize(i["lVal18AFC"]) == word_normalize(symbol)
            ) and (i["lastDate"] == 1):
                return i["insCode"]
        raise ValueError(f"Cannot find {symbol!r}. Enter valid symbol.")

    @staticmethod
    def _handle_ins_cod_or_symbol(func):
        @functools.wraps(func)
        def wrapper(self, symbol, ins_code: InsCode):
            if symbol:
                if isinstance(symbol, list):
                    symbol = [self.search_ins_code(i) for i in symbol]
                else:
                    symbol = self.search_ins_code(symbol)
            return func(self, symbol, ins_code)

        return wrapper

    @_handle_ins_cod_or_symbol
    def ins_info(self, symbol: Symbol = None, ins_code: InsCode = None):
        """
        .. raw:: html

            <div dir="rtl">
                کدِ صفحه‌ی نماد/ابزارِ-معاملاتی رو استخراج می‌کنه.
            </div>

        Parameters
        ----------
        symbol: Symbol
        ins_code: InsCode
            نماد

        Returns
        -------
        """
        ins_code = symbol if symbol else ins_code
        if isinstance(ins_code, list):
            url = [self.url.ins_info(i) for i in ins_code]
            r = self.requests(url)
        else:
            r = self.requests(self.url.ins_info(ins_code))


