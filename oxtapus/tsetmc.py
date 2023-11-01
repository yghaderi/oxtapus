import functools
import re
import polars as pl
from tarix.dateutils import dateutils

from oxtapus.utils.http import requests, async_requests
from oxtapus.utils import json_normalize, word_normalize, manipulation_cols
from oxtapus.utils.tsetmc import URL, cols, CED

InsCode = int | list[int] | str | list[str]
Symbol = str | list[str] | None


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
        r = self.requests(self.url.mw(sections), response="json")[0].get("marketwatch")
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

        def _expiration_date(s: str):
            ex_date = re.findall("[0-9]+", s)
            ex_date = "".join(ex_date)
            match len(ex_date):
                case 8:
                    return f"{ex_date[:4]}-{ex_date[4:6]}-{ex_date[6:8]}"
                case 6:
                    return f"14{ex_date[:2]}-{ex_date[2:4]}-{ex_date[4:6]}"

        o_df = manipulation_cols(self.mw(["options"]), cols=cols.options_mw).with_columns(
            pl.col("ins_id").str.slice(4, length=4).alias("key")
        )
        ua_df = (manipulation_cols(self.mw(["stock", "etf"]), cols=cols.options_ua_mw)
                 .filter(pl.col("ua_ob_level") == 1)
                 .with_columns(pl.col("ua_ins_id").str.slice(4, length=4).alias("key")))
        df = o_df.join(ua_df, on="key", how="inner")
        df = df.with_columns(
            [
                pl.col("name")
                .str.splitn("-", 3)
                .struct.rename_fields(["-", "k", "ex_date"])
                .alias("fields"),
            ]
        ).unnest("fields").with_columns(
            ex_date=pl.col("ex_date").map_elements(_expiration_date)
        ).drop("-")

        df = df.with_columns(
            type=pl.when(pl.col("symbol").str.slice(0) == "ض").then("call").otherwise("put"),
            t=pl.col("ex_date").map_elements(lambda x: dateutils.days(end=x))
        )
        return df

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
        r = self.requests(self.url.search_ins_code(symbol))[0]["instrumentSearch"]
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
            return pl.DataFrame([CED.ins_info(i.get("instrumentInfo") for i in r)])

        r = self.requests(self.url.ins_info(ins_code))
        return pl.DataFrame(r.get("instrumentInfo"))
