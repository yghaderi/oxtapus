import functools
import re
import polars as pl
from typing import List
from urllib.parse import urlencode
from tarix.dateutils import dateutils

from oxtapus.utils.http import requests, async_requests
from oxtapus.utils import json_normalize, word_normalize, manipulation_cols, cols


class URL:
    def __init__(self, base_url="http://cdn.tsetmc.com/api"):
        self.base_url = base_url

    def mw(self, sections: List[str]):
        """
        .. raw:: html

            <div dir="rtl">
                لینکِ مارکت-واچ رو بر اساسِ بخش‌هایی که می‌خواین می‌سازه.
            </div>

        Parameters
        ----------
        sections: list[str]
            - stock: سهام
            - ifb_paye: پایه-فرابورس
            - mortgage: اوراقِ مسکن
            - cum_right: حقِ-تقدم
            - bond: اوراقِ بدهی
            - options: اختیارِ معامله
            - futures: آتی
            - etf: صندوق‌هایِ قابلِ-معامله
            - commodity: کالا

        Returns
        -------
        url: str
        """
        papers = {}
        for i, item in enumerate(sections):
            match item.lower():
                case "stock":
                    papers[f"paperTypes[{i}]"] = 1
                case "ifb_paye":
                    papers[f"paperTypes[{i}]"] = 2
                case "mortgage":
                    papers[f"paperTypes[{i}]"] = 3
                case "cum_right":
                    papers[f"paperTypes[{i}]"] = 4
                case "bond":
                    papers[f"paperTypes[{i}]"] = 5
                case "options":
                    papers[f"paperTypes[{i}]"] = 6
                case "futures":
                    papers[f"paperTypes[{i}]"] = 7
                case "etf":
                    papers[f"paperTypes[{i}]"] = 8
                case "commodity":
                    papers[f"paperTypes[{i}]"] = 9

        param = {
            "market": 0,
            "industrialGroup": "",
            **papers,
            "showTraded": "false",
            "withBestLimits": "true",
        }
        return f"{self.base_url}/ClosingPrice/GetMarketWatch?{urlencode(param)}"

    def search_ins_code(self, symbol_far):
        """
        .. raw:: html

            <div dir="rtl">
                لینکِ جست-و-جوی نماد رو می‌سازه.
            </div>

        Parameters
        ----------
        symbol_far: str
            نمادِ فارسی

        Returns
        -------
        url: str
        """
        return f"{self.base_url}/Instrument/getinstrumentsearch/{symbol_far}"

    def ins_info(self, ins_code: int | str):
        """
        .. raw:: html

            <div dir="rtl">
                لینکِ داده‌هایِ مربوط به نماد رو می‌سازه.
            </div>

        Parameters
        ----------
        ins_code: int|str
            کدِ صفحه‌یِ نماد (عددِ انتهایِ لینکِ صفحه‌یِ نماد)

        Returns
        -------
        url: str
        """
        return f"{self.base_url}/Instrument/GetInstrumentInfo/{ins_code}"

    def hist_price(self, ins_code):
        """
        .. raw:: html

            <div dir="rtl">
                لینکِ داده‌هایِ مربوط به قیمتِ تاریخیِ نماد رو می‌سازه.
            </div>

        Parameters
        ----------
        ins_code: int|str
            کدِ صفحه‌یِ نماد (عددِ انتهایِ لینکِ صفحه‌یِ نماد)

        Returns
        -------
        url: str
        """
        return f"{self.base_url}/ClosingPrice/GetClosingPriceDailyList/{ins_code}/0"

    def client_type(self, ins_code):
        """
        .. raw:: html

            <div dir="rtl">
                لینکِ داده‌هایِ مربوط به حقیقی-حقوقیِ نماد رو می‌سازه.
            </div>

        Parameters
        ----------
        ins_code: int|str
            کدِ صفحه‌یِ نماد (عددِ انتهایِ لینکِ صفحه‌یِ نماد)

        Returns
        -------
        url: str
        """
        return f"{self.base_url}/ClientType/GetClientTypeHistory/{ins_code}"

    def share_change(self, ins_code):
        """
        .. raw:: html

            <div dir="rtl">
                لینکِ داده‌هایِ مربوط به تغییرِ سرمایه‌یِ نماد رو می‌سازه.
            </div>

        Parameters
        ----------
        ins_code: int|str
            کدِ صفحه‌یِ نماد (عددِ انتهایِ لینکِ صفحه‌یِ نماد)

        Returns
        -------
        url: str
        """
        return f"{self.base_url}/Instrument/GetInstrumentShareChange/{ins_code}"

    def specific_option_data(self, ins_id):
        """
        .. raw:: html

            <div dir="rtl">
                لینکِ مربوط به داده هایِ خاصِّ اخیارِ-معامله رو می‌سازه
            </div>

        Parameters
        ----------
        ins_id: str
            کدِ 12 رقمیِ نماد

        Returns
        -------
        url: str
        """
        return f"{self.base_url}/Instrument/GetInstrumentOptionByInstrumentID/{ins_id}"

    def all_index(self):
        return f"{self.base_url}/Index/GetIndexB1LastAll/All/1"

    def index_ticker_symbols(self, index_code):
        return f"{self.base_url}/ClosingPrice/GetIndexCompany/{index_code}"

    def index_hist(self, index_code):
        return f"{self.base_url}/Index/GetIndexB2History/{index_code}"

    def intraday_trades(self, ins_code):
        return f"{self.base_url}/Trade/GetTrade/{ins_code}"

    def last_ins_info(self, ins_code):
        return f"{self.base_url}/ClosingPrice/GetClosingPriceInfo/{ins_code}"

    def last_market_activity(self):
        return f"{self.base_url}/MarketData/GetMarketOverview/1"


class TSETMC:
    def __init__(self, async_req: bool = False):
        self._async_req = async_req
        self.requests = async_requests if self._async_req else requests
        self.url = URL()

    @property
    def async_req(self):
        return self._async_req

    @async_req.setter
    def async_req(self, async_req):
        self._async_req = async_req
        if async_req:
            self.requests = async_requests
        else:
            self.requests = requests

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
        df = pl.from_dicts(
            json_normalize(r, "blDs", "ob_"), schema_overrides={"pe": pl.Utf8}
        )
        df = manipulation_cols(df, columns=cols.tsetmc.mw_orderbook)
        df = manipulation_cols(df, columns=cols.tsetmc.mw)
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

        o_df = (
            manipulation_cols(self.mw(["options"]), columns=cols.tsetmc.options_mw)
            .filter(
                (
                    pl.col("symbol").str.starts_with("ض")
                    | pl.col("symbol").str.starts_with("ط")
                )
                & ((pl.col("ask_size") > 0) | (pl.col("bid_size") > 0))
            )
            .with_columns(pl.col("ins_id").str.slice(4, length=4).alias("key"))
        )
        ua_df = (
            manipulation_cols(
                self.mw(["stock", "etf"]), columns=cols.tsetmc.options_ua_mw
            )
            .filter(pl.col("ua_ob_level") == 1)
            .with_columns(pl.col("ua_ins_id").str.slice(4, length=4).alias("key"))
        )
        df = o_df.join(ua_df, on="key", how="inner")
        df = (
            df.with_columns(
                [
                    pl.col("name")
                    .str.splitn("-", 3)
                    .struct.rename_fields(["-", "k", "ex_date"])
                    .alias("fields"),
                ]
            )
            .unnest("fields")
            .with_columns(ex_date=pl.col("ex_date").map_elements(_expiration_date))
            .drop("-")
        )

        df = df.with_columns(
            k=pl.col("k").cast(pl.Int64),
            type=pl.when(pl.col("symbol").str.slice(0) == "ض")
            .then("call")
            .otherwise("put"),
            t=pl.col("ex_date").map_elements(lambda x: dateutils.days(end=x)),
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
            if (word_normalize(i["lVal18AFC"]) == word_normalize(symbol)) and (
                i["lastDate"] == 1
            ):
                return i["insCode"]
        raise ValueError(f"Cannot find {symbol!r}. Enter valid symbol.")

    @staticmethod
    def _handle_ins_cod_or_symbol(func):
        @functools.wraps(func)
        def wrapper(self, symbol=None, ins_code=None):
            if symbol:
                if isinstance(symbol, list):
                    symbol = [self.search_ins_code(i) for i in symbol]
                else:
                    symbol = self.search_ins_code(symbol)
            return func(self, symbol, ins_code)

        return wrapper

    @_handle_ins_cod_or_symbol
    def ins_info(
        self,
        symbol: str | list[str] | None = None,
        ins_code: str | list[str] | None = None,
    ):
        """
        .. raw:: html

            <div dir="rtl">
                داده‌هایِ پایه‌‌یِ نماد/ابزارِ-معاملاتی رو استخراج می‌کنه.
            </div>

        .. warning::
            .. raw:: html

                <div dir="rtl">
                    زمانِ استخراجِ داده با استفاده از
                    <span style="color:#ec4899">ins_code</span>
                    تقریبن نصفِ استفاده از
                    <span style="color:#ec4899">symbol</span>
                    است.
                    پس بهتره که اطلاعاتِ پایه‌یِ نماد رو در جایی ذخیره کنی و با استفاده از
                    <span style="color:#ec4899">ins_code</span> داده استخراج کنی.
                </div>

        .. note::
            .. raw:: html

                <div dir="rtl">
                    یا
                    <span style="color:#ec4899">ins_code</span>
                    رو وارد کن، یا
                    <span style="color:#ec4899">symbol</span>
                    رو.
                اگه هر دو رو وارد کنی،
                    <span style="color:#ec4899">symbol</span>
                نادیده گرفته می‌شه و تنها از
                    <span style="color:#ec4899">ins_code</span>
                    استفاده می‌شه. پس الکی‌ خودتو زحمت نده!
                </div>


        Parameters
        ----------
        symbol: str | list[str] | None
            نماد
        ins_code: str | list[str] | None
            کدِ 12 رقمیِ نماد

        Returns
        -------
        polars.DataFrame

        example
        ------
        >>> from oxtapus import TSETMC
        >>> tsetmc = TSETMC(async_req=True)
        >>> tsetmc.ins_info(ins_code = ["7745894403636165", "65883838195688438"])
        shape: (2, 17)
        ┌────────────┬────────────┬───────────┬────────────┬───┬──────────┬───────┬────────────┬───────────┐
        │ ins_code   ┆ ins_id     ┆ symbol_en ┆ name_en    ┆ … ┆ base_vol ┆ eps   ┆ pct_float_ ┆ contract_ │
        │ ---        ┆ ---        ┆ ---       ┆ ---        ┆   ┆ ---      ┆ ---   ┆ shares     ┆ size      │
        │ str        ┆ str        ┆ str       ┆ str        ┆   ┆ i64      ┆ str   ┆ ---        ┆ ---       │
        │            ┆            ┆           ┆            ┆   ┆          ┆       ┆ str        ┆ i64       │
        ╞════════════╪════════════╪═══════════╪════════════╪═══╪══════════╪═══════╪════════════╪═══════════╡
        │ 7745894403 ┆ IRO1PNES00 ┆ PNES      ┆ S*Isf. Oil ┆ … ┆ 14760148 ┆ 1675  ┆ 43         ┆ 0         │
        │ 636165     ┆ 01         ┆           ┆ Ref.Co.    ┆   ┆          ┆       ┆            ┆           │
        │ 6588383819 ┆ IRO1IKCO00 ┆ IKCO      ┆ Iran       ┆ … ┆ 51746442 ┆ -1359 ┆ 36         ┆ 0         │
        │ 5688438    ┆ 01         ┆           ┆ Khodro     ┆   ┆          ┆       ┆            ┆           │
        └────────────┴────────────┴───────────┴────────────┴───┴──────────┴───────┴────────────┴───────────┘

        >>> tsetmc.ins_info(symbol = ["شپنا", "خودرو"])
        shape: (2, 17)
        ┌────────────┬────────────┬───────────┬────────────┬───┬──────────┬───────┬────────────┬───────────┐
        │ ins_code   ┆ ins_id     ┆ symbol_en ┆ name_en    ┆ … ┆ base_vol ┆ eps   ┆ pct_float_ ┆ contract_ │
        │ ---        ┆ ---        ┆ ---       ┆ ---        ┆   ┆ ---      ┆ ---   ┆ shares     ┆ size      │
        │ str        ┆ str        ┆ str       ┆ str        ┆   ┆ i64      ┆ str   ┆ ---        ┆ ---       │
        │            ┆            ┆           ┆            ┆   ┆          ┆       ┆ str        ┆ i64       │
        ╞════════════╪════════════╪═══════════╪════════════╪═══╪══════════╪═══════╪════════════╪═══════════╡
        │ 7745894403 ┆ IRO1PNES00 ┆ PNES      ┆ S*Isf. Oil ┆ … ┆ 14760148 ┆ 1675  ┆ 43         ┆ 0         │
        │ 636165     ┆ 01         ┆           ┆ Ref.Co.    ┆   ┆          ┆       ┆            ┆           │
        │ 6588383819 ┆ IRO1IKCO00 ┆ IKCO      ┆ Iran       ┆ … ┆ 51746442 ┆ -1359 ┆ 36         ┆ 0         │
        │ 5688438    ┆ 01         ┆           ┆ Khodro     ┆   ┆          ┆       ┆            ┆           │
        └────────────┴────────────┴───────────┴────────────┴───┴──────────┴───────┴────────────┴───────────┘
        """

        def map_json(data: dict):
            return {
                "ins_code": data["insCode"],
                "ins_id": data["instrumentID"],
                "symbol_en": data["cIsin"][4:8],
                "name_en": data["lVal18"],
                "symbol": data["lVal18AFC"],
                "name": data["lVal30"],
                "capital": data["zTitad"],
                "sector_name": data["sector"]["lSecVal"],
                "sector_code": data["sector"]["cSecVal"].replace(" ", ""),
                "group_type": data["cgrValCot"],
                "market_name": data["flowTitle"],
                "market_code": data["flow"],
                "market_type": data["cgrValCotTitle"],
                "base_vol": data["baseVol"],
                "eps": data["eps"]["estimatedEPS"],
                "pct_float_shares": data["kAjCapValCpsIdx"],
                "contract_size": data["contractSize"],
            }

        ins_code = symbol if symbol else ins_code

        if isinstance(ins_code, str):
            ins_code = [ins_code]
        url = [self.url.ins_info(i) for i in ins_code]
        r = self.requests(url)
        return pl.from_records([map_json(i.get("instrumentInfo")) for i in r])

    def specific_option_data(self, ins_id: str | list[str]):
        """
        Get complimentary option info.

        Parameters
        ----------
        ins_id
            کدِ 12 رقمیِ نماد

        Returns
        -------
        polars.DataFrame

        example
        -------
        >>> from oxtapus import TSETMC
        >>> tsetmc = TSETMC()
        >>> tsetmc.specific_option_data(["IRO9IKCO2851", "IRO9IKCO20K1"])
        shape: (2, 7)
        ┌──────────────────┬───────────────────┬────────────┬──────────┬──────────┬────────┬───────────────┐
        │ ins_code         ┆ ua_ins_code       ┆ begin_date ┆ ex_date  ┆ lot_size ┆ k      ┆ open_interest │
        │ ---              ┆ ---               ┆ ---        ┆ ---      ┆ ---      ┆ ---    ┆ ---           │
        │ str              ┆ str               ┆ i64        ┆ i64      ┆ i64      ┆ f64    ┆ i64           │
        ╞══════════════════╪═══════════════════╪════════════╪══════════╪══════════╪════════╪═══════════════╡
        │ 8907495648806531 ┆ 65883838195688438 ┆ 20230930   ┆ 20240221 ┆ 1000     ┆ 2600.0 ┆ 1006          │
        │ 4785638272776115 ┆ 65883838195688438 ┆ 20231028   ┆ 20240327 ┆ 1000     ┆ 3750.0 ┆ 0             │
        └──────────────────┴───────────────────┴────────────┴──────────┴──────────┴────────┴───────────────┘
        """
        if isinstance(ins_id, str):
            ins_id = [ins_id]
        url = [self.url.specific_option_data(i) for i in ins_id]
        r = requests(url)
        df = pl.from_records([i.get("instrumentOption") for i in r])
        df = manipulation_cols(df, columns=cols.tsetmc.specific_option_data)
        return df

    @_handle_ins_cod_or_symbol
    def hist_price(
        self,
        symbol: str | list[str] | None = None,
        ins_code: str | list[str] | None = None,
        start: str | None = None,
        end: str | None = None,
    ):
        """
        .. raw:: html

            <div dir="rtl">
                داده‌هایِ تاریخیِ مروبط به معامله‌یِ نماد رو استخراج می‌کنه.
            </div>

        .. warning::
            .. raw:: html

                <div dir="rtl">
                    زمانِ استخراجِ داده با استفاده از
                    <span style="color:#ec4899">ins_code</span>
                    تقریبن نصفِ استفاده از
                    <span style="color:#ec4899">symbol</span>
                    است.
                    پس بهتره که اطلاعاتِ پایه‌یِ نماد رو در جایی ذخیره کنی و با استفاده از
                    <span style="color:#ec4899">ins_code</span> داده استخراج کنی.
                </div>

        .. note::
            .. raw:: html

                <div dir="rtl">
                    یا
                    <span style="color:#ec4899">ins_code</span>
                    رو وارد کن، یا
                    <span style="color:#ec4899">symbol</span>
                    رو.
                اگه هر دو رو وارد کنی،
                    <span style="color:#ec4899">symbol</span>
                نادیده گرفته می‌شه و تنها از
                    <span style="color:#ec4899">ins_code</span>
                    استفاده می‌شه. پس الکی‌ خودتو زحمت نده!
                </div>

        Parameters
        ----------
        symbol: str | list[str] | None
            نماد
        ins_code: str | list[str] | None
            کدِ 12 رقمیِ نماد

        start: str, default None
            تاریخِ شروع(جلالی).
            اگه هیچی داده نشه، داده‌ها از روزِ اول استخراج می‌شن.
                format: 'yyyymmdd', 'yyyy-mm-dd', 'yyyy/mm/dd', e.g. '1402-05-25'

        end: str
            تاریخِ پایان(جلالی).
            اگه هیچی داده نشه، داده‌ها تا روزِ آخر استخراج می‌شن.
                format: 'yyyymmdd', 'yyyy-mm-dd', 'yyyy/mm/dd', e.g. '1402-08-05'

        Returns
        -------
        polars.DataFrame

        example
        -------
        >>> from oxtapus import TSETMC
        >>> tsetmc = TSETMC(async_req=True)
        >>> tsetmc.hist_price(symbol = ["شپنا", "فملی"])
        shape: (7_629, 11)
        ┌───────────────────┬────────────┬────────┬────────┬───┬─────────┬──────────────┬───────────┬─────────────┐
        │ ins_code          ┆ date       ┆ open   ┆ high   ┆ … ┆ y_final ┆ volume       ┆ value     ┆ trade_count │
        │ ---               ┆ ---        ┆ ---    ┆ ---    ┆   ┆ ---     ┆ ---          ┆ ---       ┆ ---         │
        │ str               ┆ date       ┆ f64    ┆ f64    ┆   ┆ f64     ┆ f64          ┆ f64       ┆ f64         │
        ╞═══════════════════╪════════════╪════════╪════════╪═══╪═════════╪══════════════╪═══════════╪═════════════╡
        │ 7745894403636165  ┆ 2008-06-29 ┆ 5800.0 ┆ 5800.0 ┆ … ┆ 0.0     ┆ 1.89389047e8 ┆ 1.0985e12 ┆ 5685.0      │
        │ 7745894403636165  ┆ 2008-06-30 ┆ 5974.0 ┆ 5974.0 ┆ … ┆ 5800.0  ┆ 1.9643005e7  ┆ 1.1685e11 ┆ 2021.0      │
        │ 7745894403636165  ┆ 2008-07-01 ┆ 5829.0 ┆ 5839.0 ┆ … ┆ 5948.0  ┆ 2.2646072e7  ┆ 1.3157e11 ┆ 805.0       │
        │ 7745894403636165  ┆ 2008-07-02 ┆ 5869.0 ┆ 5982.0 ┆ … ┆ 5808.0  ┆ 3.591428e6   ┆ 2.1308e10 ┆ 551.0       │
        │ …                 ┆ …          ┆ …      ┆ …      ┆ … ┆ …       ┆ …            ┆ …         ┆ …           │
        │ 35425587644337450 ┆ 2023-10-29 ┆ 6810.0 ┆ 6950.0 ┆ … ┆ 6830.0  ┆ 4.195696e7   ┆ 2.8863e11 ┆ 2388.0      │
        │ 35425587644337450 ┆ 2023-10-30 ┆ 6880.0 ┆ 6990.0 ┆ … ┆ 6880.0  ┆ 2.1627873e7  ┆ 1.4942e11 ┆ 2211.0      │
        │ 35425587644337450 ┆ 2023-10-31 ┆ 6920.0 ┆ 6950.0 ┆ … ┆ 6910.0  ┆ 3.6062861e7  ┆ 2.4930e11 ┆ 1956.0      │
        │ 35425587644337450 ┆ 2023-11-01 ┆ 6890.0 ┆ 6920.0 ┆ … ┆ 6910.0  ┆ 4.663197e7   ┆ 3.2148e11 ┆ 2028.0      │
        └───────────────────┴────────────┴────────┴────────┴───┴─────────┴──────────────┴───────────┴─────────────┘

        >>> tsetmc.async_req = False
        >>> tsetmc.hist_price(ins_code = ["7745894403636165", "35425587644337450"])
        shape: (7_629, 11)
        ┌───────────────────┬────────────┬────────┬────────┬───┬─────────┬──────────────┬───────────┬─────────────┐
        │ ins_code          ┆ date       ┆ open   ┆ high   ┆ … ┆ y_final ┆ volume       ┆ value     ┆ trade_count │
        │ ---               ┆ ---        ┆ ---    ┆ ---    ┆   ┆ ---     ┆ ---          ┆ ---       ┆ ---         │
        │ str               ┆ date       ┆ f64    ┆ f64    ┆   ┆ f64     ┆ f64          ┆ f64       ┆ f64         │
        ╞═══════════════════╪════════════╪════════╪════════╪═══╪═════════╪══════════════╪═══════════╪═════════════╡
        │ 7745894403636165  ┆ 2008-06-29 ┆ 5800.0 ┆ 5800.0 ┆ … ┆ 0.0     ┆ 1.89389047e8 ┆ 1.0985e12 ┆ 5685.0      │
        │ 7745894403636165  ┆ 2008-06-30 ┆ 5974.0 ┆ 5974.0 ┆ … ┆ 5800.0  ┆ 1.9643005e7  ┆ 1.1685e11 ┆ 2021.0      │
        │ 7745894403636165  ┆ 2008-07-01 ┆ 5829.0 ┆ 5839.0 ┆ … ┆ 5948.0  ┆ 2.2646072e7  ┆ 1.3157e11 ┆ 805.0       │
        │ 7745894403636165  ┆ 2008-07-02 ┆ 5869.0 ┆ 5982.0 ┆ … ┆ 5808.0  ┆ 3.591428e6   ┆ 2.1308e10 ┆ 551.0       │
        │ …                 ┆ …          ┆ …      ┆ …      ┆ … ┆ …       ┆ …            ┆ …         ┆ …           │
        │ 35425587644337450 ┆ 2023-10-29 ┆ 6810.0 ┆ 6950.0 ┆ … ┆ 6830.0  ┆ 4.195696e7   ┆ 2.8863e11 ┆ 2388.0      │
        │ 35425587644337450 ┆ 2023-10-30 ┆ 6880.0 ┆ 6990.0 ┆ … ┆ 6880.0  ┆ 2.1627873e7  ┆ 1.4942e11 ┆ 2211.0      │
        │ 35425587644337450 ┆ 2023-10-31 ┆ 6920.0 ┆ 6950.0 ┆ … ┆ 6910.0  ┆ 3.6062861e7  ┆ 2.4930e11 ┆ 1956.0      │
        │ 35425587644337450 ┆ 2023-11-01 ┆ 6890.0 ┆ 6920.0 ┆ … ┆ 6910.0  ┆ 4.663197e7   ┆ 3.2148e11 ┆ 2028.0      │
        └───────────────────┴────────────┴────────┴────────┴───┴─────────┴──────────────┴───────────┴─────────────┘
        """

        ins_code = symbol if symbol else ins_code
        if isinstance(ins_code, str):
            ins_code = [ins_code]
        url = [self.url.hist_price(i) for i in ins_code]
        r = requests(url)
        df = pl.DataFrame()
        for resp in r:
            df_ = pl.from_records(resp.get("closingPriceDaily"), orient="col")
            df_ = (
                manipulation_cols(df_, columns=cols.tsetmc.hist_price)
                .with_columns(pl.col("date").cast(pl.Utf8).str.to_date(format="%Y%m%d"))
                .sort("date")
            )
            df = pl.concat([df, df_])
        return df

    def adj_hist_price(
        self,
        symbol: str | list[str] | None = None,
        ins_code: str | list[str] | None = None,
        start: str | None = None,
        end: str | None = None,
    ):
        """
        .. raw:: html

            <div dir="rtl">
                داده‌هایِ تاریخیِ مروبط به معامله‌یِ نماد رو استخراج  و به صورتِ تعدیلی برمیگردونه.
            </div>

        .. warning::
            .. raw:: html

                <div dir="rtl">
                    زمانِ استخراجِ داده با استفاده از
                    <span style="color:#ec4899">ins_code</span>
                    تقریبن نصفِ استفاده از
                    <span style="color:#ec4899">symbol</span>
                    است.
                    پس بهتره که اطلاعاتِ پایه‌یِ نماد رو در جایی ذخیره کنی و با استفاده از
                    <span style="color:#ec4899">ins_code</span> داده استخراج کنی.
                </div>

        .. note::
            .. raw:: html

                <div dir="rtl">
                    یا
                    <span style="color:#ec4899">ins_code</span>
                    رو وارد کن، یا
                    <span style="color:#ec4899">symbol</span>
                    رو.
                اگه هر دو رو وارد کنی،
                    <span style="color:#ec4899">symbol</span>
                نادیده گرفته می‌شه و تنها از
                    <span style="color:#ec4899">ins_code</span>
                    استفاده می‌شه. پس الکی‌ خودتو زحمت نده!
                </div>

        Parameters
        ----------
        symbol: str | list[str] | None
            نماد
        ins_code: str | list[str] | None
            کدِ 12 رقمیِ نماد

        start: str, default None
            تاریخِ شروع(جلالی).
            اگه هیچی داده نشه، داده‌ها از روزِ اول استخراج می‌شن.
                format: 'yyyymmdd', 'yyyy-mm-dd', 'yyyy/mm/dd', e.g. '1402-05-25'

        end: str
            تاریخِ پایان(جلالی).
            اگه هیچی داده نشه، داده‌ها تا روزِ آخر استخراج می‌شن.
                format: 'yyyymmdd', 'yyyy-mm-dd', 'yyyy/mm/dd', e.g. '1402-08-05'

        Returns
        -------
        polars.DataFrame

        example
        -------
        >>> from oxtapus import TSETMC
        >>> tsetmc = TSETMC()
        >>> tsetmc.adj_hist_price(ins_code = ["7745894403636165", "35425587644337450"])
        shape: (7_629, 16)
        ┌───────────────────┬────────────┬────────┬────────┬───┬────────────┬────────────┬────────────┬────────────┐
        │ ins_code          ┆ date       ┆ open   ┆ high   ┆ … ┆ adj_high   ┆ adj_low    ┆ adj_close  ┆ adj_final  │
        │ ---               ┆ ---        ┆ ---    ┆ ---    ┆   ┆ ---        ┆ ---        ┆ ---        ┆ ---        │
        │ str               ┆ date       ┆ f64    ┆ f64    ┆   ┆ f64        ┆ f64        ┆ f64        ┆ f64        │
        ╞═══════════════════╪════════════╪════════╪════════╪═══╪════════════╪════════════╪════════════╪════════════╡
        │ 7745894403636165  ┆ 2008-06-29 ┆ 5800.0 ┆ 5800.0 ┆ … ┆ 122.756414 ┆ 122.756414 ┆ 122.756414 ┆ 122.756414 │
        │ 7745894403636165  ┆ 2008-06-30 ┆ 5974.0 ┆ 5974.0 ┆ … ┆ 126.439106 ┆ 122.777579 ┆ 125.888819 ┆ 125.888819 │
        │ 7745894403636165  ┆ 2008-07-01 ┆ 5829.0 ┆ 5839.0 ┆ … ┆ 123.581845 ┆ 122.544765 ┆ 122.925733 ┆ 122.925733 │
        │ 7745894403636165  ┆ 2008-07-02 ┆ 5869.0 ┆ 5982.0 ┆ … ┆ 126.608426 ┆ 122.925733 ┆ 125.571346 ┆ 125.571346 │
        │ …                 ┆ …          ┆ …      ┆ …      ┆ … ┆ …          ┆ …          ┆ …          ┆ …          │
        │ 35425587644337450 ┆ 2023-10-29 ┆ 6810.0 ┆ 6950.0 ┆ … ┆ 6950.0     ┆ 6790.0     ┆ 6950.0     ┆ 6880.0     │
        │ 35425587644337450 ┆ 2023-10-30 ┆ 6880.0 ┆ 6990.0 ┆ … ┆ 6990.0     ┆ 6860.0     ┆ 6910.0     ┆ 6910.0     │
        │ 35425587644337450 ┆ 2023-10-31 ┆ 6920.0 ┆ 6950.0 ┆ … ┆ 6950.0     ┆ 6900.0     ┆ 6910.0     ┆ 6910.0     │
        │ 35425587644337450 ┆ 2023-11-01 ┆ 6890.0 ┆ 6920.0 ┆ … ┆ 6920.0     ┆ 6810.0     ┆ 6920.0     ┆ 6890.0     │
        └───────────────────┴────────────┴────────┴────────┴───┴────────────┴────────────┴────────────┴────────────┘
        """
        ins_code = symbol if symbol else ins_code
        if isinstance(ins_code, str):
            ins_code = [ins_code]

        df = self.hist_price(ins_code=ins_code)
        df = (
            df.with_columns(
                factor=(pl.col("y_final").shift(-1) / pl.col("final"))
                .fill_null(1)
                .reverse()
                .cumprod()
                .reverse()
                .over("ins_code")
            )
            .with_columns(
                adj_open=pl.col("open").mul(pl.col("factor")),
                adj_high=pl.col("high").mul(pl.col("factor")),
                adj_low=pl.col("low").mul(pl.col("factor")),
                adj_close=pl.col("close").mul(pl.col("factor")),
                adj_final=pl.col("final").mul(pl.col("factor")),
            )
            .drop("factor")
        )
        return df
