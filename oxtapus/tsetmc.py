import functools
import datetime
from enum import Enum
import polars as pl
from typing import List
from pydantic import validate_call
from urllib.parse import urlencode
import itertools
from oxtapus.models.tsetmc import HistPrice, MarketWatch, ClientTypeAll, InsInfo

from oxtapus.utils.http import get, async_requests
from oxtapus.utils import (
    json_normalize,
    word_normalize,
    manipulation_cols,
    cols,
    normalize_nested_dict,
)
from oxtapus.utils.models import AdjustPriceFlow, InsShareChangeFlow, OptionsMW


__all__ = ["TSETMC", "MWSections"]


class MWSections(str, Enum):
    stock = "stock"
    ifb_paye = "ifb_paye"
    mortgage = "mortgage"
    cum_right = "cum_right"
    bond = "bond"
    options = "options"
    futures = "futures"
    etf = "etf"
    commodity = "commodity"


class URL:
    def __init__(self, base_url="https://cdn.tsetmc.com/api"):
        self.base_url = base_url

    @validate_call
    def mw(self, sections: List[MWSections] | MWSections) -> str:
        """
        .. raw:: html

            <div dir="rtl">
                لینکِ مارکت-واچ رو بر اساسِ بخش‌هایی که می‌خواین می‌سازه.
            </div>

        Parameters
        ----------
        sections: List[MWSections]  or MWSections
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
        if isinstance(sections, str):
            sections = [sections]
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

    def client_type_all(self):
        return f"{self.base_url}/ClientType/GetClientTypeAll"

    def search_ins_code(self, symbol_far) -> str:
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

    def ins_info(self, ins_code: int | str) -> str:
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

    def hist_price(self, ins_code) -> str:
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

    def client_type(self, ins_code) -> str:
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

    def share_change(self, ins_code) -> str:
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

    def specific_option_data(self, ins_id) -> str:
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

    def indexes(self) -> str:
        return f"{self.base_url}/Index/GetIndexB1LastAll/All/1"

    def symbols_that_index_tracks(self, index_code) -> str:
        return f"{self.base_url}/ClosingPrice/GetIndexCompany/{index_code}"

    def index_hist(self, index_code) -> str:
        return f"{self.base_url}/Index/GetIndexB2History/{index_code}"

    def intraday_trades(self, ins_code) -> str:
        return f"{self.base_url}/Trade/GetTrade/{ins_code}"

    def intraday_trades_hist(self, ins_code, date) -> str:
        return f"{self.base_url}/Trade/GetTradeHistory/{ins_code}/{date}/true"

    def orderbook_hist(self, ins_code, date) -> str:
        return f"{self.base_url}/BestLimits/{ins_code}/{date}"

    def last_ins_data(self, ins_code) -> str:
        return f"{self.base_url}/ClosingPrice/GetClosingPriceInfo/{ins_code}"

    def last_market_activity(self) -> str:
        return f"{self.base_url}/MarketData/GetMarketOverview/1"

    def shareholder_list(self, ins_code) -> str:
        return f"{self.base_url}/Shareholder/GetInstrumentShareHolderLast/{ins_code}"

    def tse_adjust_price_flow(self, last_records: int) -> str:
        return f"{self.base_url}/ClosingPrice/GetPriceAdjustByFlow/1/{last_records}"

    def ifb_adjust_price_flow(self, last_records: int) -> str:
        return f"{self.base_url}/ClosingPrice/GetPriceAdjustByFlow/2/{last_records}"

    def tse_share_change_flow(self) -> str:
        return f"{self.base_url}/Instrument/GetInstrumentShareChangeByFlow/1/9999"

    def ifb_share_change_flow(self) -> str:
        return f"{self.base_url}/Instrument/GetInstrumentShareChangeByFlow/2/9999"

    def options_mw(self):
        return f"{self.base_url}/Instrument/GetInstrumentOptionMarketWatch/0"

    def tse_options_mw(self):
        return f"{self.base_url}/Instrument/GetInstrumentOptionMarketWatch/1"

    def ifb_options_mw(self):
        return f"{self.base_url}/Instrument/GetInstrumentOptionMarketWatch/2"


class TSETMC:
    """
    Parameters
    ----------
    async_req: bool, default False
    get_all_ins_code: bool, default False
            اگه 'True' باشه نمادهای حذف-شده(تغییرٍ بازار) رو هم میاره
    """

    def __init__(self, async_req: bool = False, get_all_ins_code: bool = False):
        self._async_req = async_req
        self.get_all_ins_code = get_all_ins_code
        self.requests = async_requests if self._async_req else get
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
            self.requests = get

    @validate_call
    def mw(self, sections: List[MWSections] | MWSections) -> pl.DataFrame:
        """
        .. raw:: html

            <div dir="rtl">
                مارکت-واچ رو بر اساسِ بخش‌هایی که می‌خواین استخراج می‌کنه و تمیز شده بهتون می‌ده.
            </div>

        Parameters
        ----------
        sections: List[MWSections]  or MWSections
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
        r_client_type = self.requests(self.url.client_type_all())[0]["clientTypeAllDto"]
        records = json_normalize(
            data=[MarketWatch.model_validate(i).model_dump() for i in r],
            record_path="order_book",
        )
        df = pl.DataFrame(records)
        df_ct = pl.from_dicts([ClientTypeAll(**i).model_dump() for i in r_client_type])
        df = df.join(df_ct, on=["ins_code"], how="left")
        return df

    def options_mw(self):
        """
        .. raw:: html

            <div dir="rtl">
                داده‌های نمایِ بازارِ اختیارِ-معامله‌  رو بهت می‌ده
            </div>

        Returns
        -------
        polars.DataFrame

        example
        -------
        >>> from oxtapus import TSETMC
        >>> tsetmc = TSETMC()
        >>> tsetmc.options_mw()
        shape: (1_043, 41)
        ┌───────────────────┬───────────┬──────────┬────────────┬───┬────────────────┬────────────────────────────────┬──────────┬───────────────────┐
        │ ins_code_ua       ┆ symbol_ua ┆ final_ua ┆ y_final_ua ┆ … ┆ notional_val_p ┆ name_p                         ┆ symbol_p ┆ ins_code_p        │
        │ ---               ┆ ---       ┆ ---      ┆ ---        ┆   ┆ ---            ┆ ---                            ┆ ---      ┆ ---               │
        │ str               ┆ str       ┆ i64      ┆ i64        ┆   ┆ i64            ┆ str                            ┆ str      ┆ str               │
        ╞═══════════════════╪═══════════╪══════════╪════════════╪═══╪════════════════╪════════════════════════════════╪══════════╪═══════════════════╡
        │ 17914401175772326 ┆ اهرم      ┆ 21350    ┆ 21450      ┆ … ┆ 0              ┆ اختيارف اهرم-20000-1403/02/26  ┆ طهرم2006 ┆ 13426704534326039 │
        │ 42799209630949274 ┆ بهين رو   ┆ 10620    ┆ 10750      ┆ … ┆ 0              ┆ اختيارف بهين رو-9000-03/03/30  ┆ طهين0303 ┆ 5563327722355764  │
        │ 26824673819862694 ┆ خبهمن     ┆ 1876     ┆ 1887       ┆ … ┆ 0              ┆ اختيارف خبهمن-2200-1403/01/29  ┆ طهمن0107 ┆ 33331632159155756 │
        │ 28320293733348826 ┆ وبصادر    ┆ 1777     ┆ 1799       ┆ … ┆ 0              ┆ اختيارف وبصادر-1538-1403/01/26 ┆ طصاد0103 ┆ 55072364240589915 │
        │ 62235397452612911 ┆ دارا يكم  ┆ 171090   ┆ 173320     ┆ … ┆ 0              ┆ اختيارف ص.دارا-260000-02/12/23 ┆ طدار1222 ┆ 12864975631063372 │
        │ …                 ┆ …         ┆ …        ┆ …          ┆ … ┆ …              ┆ …                              ┆ …        ┆ …                 │
        │ 35425587644337450 ┆ فملي      ┆ 7400     ┆ 7420       ┆ … ┆ 0              ┆ اختيارف فملي-5500-1403/01/19   ┆ طملي0102 ┆ 43306098146722345 │
        │ 51617145873056483 ┆ شتران     ┆ 4064     ┆ 4064       ┆ … ┆ 0              ┆ اختيارف شتران-7000-1403/01/29  ┆ طترا0110 ┆ 2414774786667555  │
        │ 2400322364771558  ┆ شستا      ┆ 1166     ┆ 1177       ┆ … ┆ 0              ┆ اختيارف شستا-512-1402/12/09    ┆ طستا1209 ┆ 4273781978909014  │
        │ 2400322364771558  ┆ شستا      ┆ 1166     ┆ 1177       ┆ … ┆ 0              ┆ اختيارف شستا-1100-1402/11/11   ┆ طستا1112 ┆ 37402330157677226 │
        │ 71483646978964608 ┆ ذوب       ┆ 4058     ┆ 4225       ┆ … ┆ 0              ┆ اختيارف ذوب-3750-1403/03/23    ┆ طذوب3029 ┆ 45991541533193147 │
        └───────────────────┴───────────┴──────────┴────────────┴───┴────────────────┴────────────────────────────────┴──────────┴───────────────────┘
        """
        r = self.requests(self.url.options_mw())
        df = pl.from_dicts(
            [OptionsMW(**i).model_dump() for i in r[0]["instrumentOptMarketWatch"]]
        )
        return df

    def tse_options_mw(self):
        """
        .. raw:: html

            <div dir="rtl">
                داده‌های نمایِ بازارِ اختیارِ-معامله‌یِ بورسِ تهران رو بهت می‌ده
            </div>

        Returns
        -------
        polars.DataFrame

        example
        -------
        >>> from oxtapus import TSETMC
        >>> tsetmc = TSETMC()
        >>> tsetmc.tse_options_mw()
        shape: (652, 41)
        ┌───────────────────┬───────────┬──────────┬────────────┬───┬────────────────┬────────────────────────────────┬──────────┬───────────────────┐
        │ ins_code_ua       ┆ symbol_ua ┆ final_ua ┆ y_final_ua ┆ … ┆ notional_val_p ┆ name_p                         ┆ symbol_p ┆ ins_code_p        │
        │ ---               ┆ ---       ┆ ---      ┆ ---        ┆   ┆ ---            ┆ ---                            ┆ ---      ┆ ---               │
        │ str               ┆ str       ┆ i64      ┆ i64        ┆   ┆ i64            ┆ str                            ┆ str      ┆ str               │
        ╞═══════════════════╪═══════════╪══════════╪════════════╪═══╪════════════════╪════════════════════════════════╪══════════╪═══════════════════╡
        │ 17914401175772326 ┆ اهرم      ┆ 21350    ┆ 21450      ┆ … ┆ 0              ┆ اختيارف اهرم-20000-1403/02/26  ┆ طهرم2006 ┆ 13426704534326039 │
        │ 42799209630949274 ┆ بهين رو   ┆ 10620    ┆ 10750      ┆ … ┆ 0              ┆ اختيارف بهين رو-9000-03/03/30  ┆ طهين0303 ┆ 5563327722355764  │
        │ 26824673819862694 ┆ خبهمن     ┆ 1876     ┆ 1887       ┆ … ┆ 0              ┆ اختيارف خبهمن-2200-1403/01/29  ┆ طهمن0107 ┆ 33331632159155756 │
        │ 28320293733348826 ┆ وبصادر    ┆ 1777     ┆ 1799       ┆ … ┆ 0              ┆ اختيارف وبصادر-1538-1403/01/26 ┆ طصاد0103 ┆ 55072364240589915 │
        │ 62235397452612911 ┆ دارا يكم  ┆ 171090   ┆ 173320     ┆ … ┆ 0              ┆ اختيارف ص.دارا-260000-02/12/23 ┆ طدار1222 ┆ 12864975631063372 │
        │ …                 ┆ …         ┆ …        ┆ …          ┆ … ┆ …              ┆ …                              ┆ …        ┆ …                 │
        │ 35425587644337450 ┆ فملي      ┆ 7400     ┆ 7420       ┆ … ┆ 0              ┆ اختيارف فملي-5500-1403/01/19   ┆ طملي0102 ┆ 43306098146722345 │
        │ 51617145873056483 ┆ شتران     ┆ 4064     ┆ 4064       ┆ … ┆ 0              ┆ اختيارف شتران-7000-1403/01/29  ┆ طترا0110 ┆ 2414774786667555  │
        │ 2400322364771558  ┆ شستا      ┆ 1166     ┆ 1177       ┆ … ┆ 0              ┆ اختيارف شستا-512-1402/12/09    ┆ طستا1209 ┆ 4273781978909014  │
        │ 2400322364771558  ┆ شستا      ┆ 1166     ┆ 1177       ┆ … ┆ 0              ┆ اختيارف شستا-1100-1402/11/11   ┆ طستا1112 ┆ 37402330157677226 │
        │ 71483646978964608 ┆ ذوب       ┆ 4058     ┆ 4225       ┆ … ┆ 0              ┆ اختيارف ذوب-3750-1403/03/23    ┆ طذوب3029 ┆ 45991541533193147 │
        └───────────────────┴───────────┴──────────┴────────────┴───┴────────────────┴────────────────────────────────┴──────────┴───────────────────┘
        """
        r = self.requests(self.url.tse_options_mw())
        df = pl.from_dicts(
            [OptionsMW(**i).model_dump() for i in r[0]["instrumentOptMarketWatch"]]
        )
        return df

    def ifb_options_mw(self):
        """
        .. raw:: html

            <div dir="rtl">
                داده‌های نمایِ بازارِ اختیارِ-معامله‌یِ فرابورس رو بهت می‌ده
            </div>

        Returns
        -------
        polars.DataFrame

        example
        -------
        >>> from oxtapus import TSETMC
        >>> tsetmc = TSETMC()
        >>> tsetmc.ifb_options_mw()
        shape: (440, 41)
        ┌───────────────────┬───────────┬──────────┬────────────┬───┬────────────────┬───────────────────────────────┬─────────────┬───────────────────┐
        │ ins_code_ua       ┆ symbol_ua ┆ final_ua ┆ y_final_ua ┆ … ┆ notional_val_p ┆ name_p                        ┆ symbol_p    ┆ ins_code_p        │
        │ ---               ┆ ---       ┆ ---      ┆ ---        ┆   ┆ ---            ┆ ---                           ┆ ---         ┆ ---               │
        │ str               ┆ str       ┆ i64      ┆ i64        ┆   ┆ i64            ┆ str                           ┆ str         ┆ str               │
        ╞═══════════════════╪═══════════╪══════════╪════════════╪═══╪════════════════╪═══════════════════════════════╪═════════════╪═══════════════════╡
        │ 58741071099161284 ┆ فرابورس   ┆ 7930     ┆ 7940       ┆ … ┆ 0              ┆ اختيارف فرابورس-9500-14030302 ┆ طفرابورس320 ┆ 66273163800167301 │
        │ 47041908051542008 ┆ هم وزن    ┆ 15965    ┆ 16007      ┆ … ┆ 0              ┆ اختيارف هم وزن-20000-14030604 ┆ طهم وزن607  ┆ 40521916202949426 │
        │ 50792786683910016 ┆ كرمان     ┆ 1285     ┆ 1323       ┆ … ┆ 0              ┆ اختيارف كرمان-1598-14021214   ┆ طكرمان1208  ┆ 57904258425842305 │
        │ 23557166059925779 ┆ فصبا      ┆ 4841     ┆ 4835       ┆ … ┆ 0              ┆ اختيارف فصبا-7300-14030115    ┆ طفصبا107    ┆ 1626986735378256  │
        │ 69067576215760005 ┆ كاريس     ┆ 22877    ┆ 22905      ┆ … ┆ 0              ┆ اختيارف كاريس-22000-14030327  ┆ طكاريس312   ┆ 55830533232484624 │
        │ …                 ┆ …         ┆ …        ┆ …          ┆ … ┆ …              ┆ …                             ┆ …           ┆ …                 │
        │ 69067576215760005 ┆ كاريس     ┆ 22877    ┆ 22905      ┆ … ┆ 0              ┆ اختيارف كاريس-32000-14030327  ┆ طكاريس317   ┆ 14799246044516392 │
        │ 47563321799863211 ┆ بتهران    ┆ 2689     ┆ 2619       ┆ … ┆ 0              ┆ اختيارف بتهران-2900-14030320  ┆ طبتهران306  ┆ 8853323062606230  │
        │ 41927452991671109 ┆ توان      ┆ 19167    ┆ 19294      ┆ … ┆ 0              ┆ اختيارف توان-19000-14021214   ┆ طتوان1204   ┆ 12757189046721683 │
        │ 41927452991671109 ┆ توان      ┆ 19167    ┆ 19294      ┆ … ┆ 0              ┆ اختيارف توان-18000-14030327   ┆ طتوان313    ┆ 43071145059933975 │
        │ 41927452991671109 ┆ توان      ┆ 19167    ┆ 19294      ┆ … ┆ 0              ┆ اختيارف توان-20000-14030327   ┆ طتوان315    ┆ 67410414240827335 │
        └───────────────────┴───────────┴──────────┴────────────┴───┴────────────────┴───────────────────────────────┴─────────────┴───────────────────┘
        """
        r = self.requests(self.url.ifb_options_mw())
        df = pl.from_dicts(
            [OptionsMW(**i).model_dump() for i in r[0]["instrumentOptMarketWatch"]]
        )
        return df

    def search_ins_code(self, symbol: str) -> list[str]:
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
        ['20562694899904339']
        """
        r = self.requests(self.url.search_ins_code(symbol))[0]["instrumentSearch"]
        if r:
            if not self.get_all_ins_code:
                return [
                    i["insCode"]
                    for i in r
                    if (word_normalize(i["lVal18AFC"]) == word_normalize(symbol))
                    and (i["lastDate"] == 1)
                ]
            return [
                i["insCode"]
                for i in r
                if word_normalize(i["lVal18AFC"]) == word_normalize(symbol)
            ]

    @staticmethod
    def _handle_ins_cod_or_symbol(func):
        @functools.wraps(func)
        def wrapper(self, symbol=None, ins_code=None):
            if symbol:
                if isinstance(symbol, list):
                    symbol = list(
                        itertools.chain(*[self.search_ins_code(i) for i in symbol])
                    )
                else:
                    symbol = self.search_ins_code(symbol)
            return func(self, symbol, ins_code)

        return wrapper

    @_handle_ins_cod_or_symbol
    def ins_info(
        self,
        symbol: str | list[str] | None = None,
        ins_code: str | list[str] | None = None,
    ) -> pl.DataFrame:
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
            کدِ صفحه‌یِ نماد

        Returns
        -------
        polars.DataFrame

        example
        ------
        >>> from oxtapus import TSETMC
        >>> tsetmc = TSETMC(async_req=True)
        >>> tsetmc.ins_info(ins_code = ["7745894403636165", "65883838195688438"])
        shape: (2, 24)
        ┌────────────┬────────────┬───────────┬────────┬───┬───────────┬───────────┬───────────┬───────────┐
        │ ins_code   ┆ ins_id     ┆ isin      ┆ symbol ┆ … ┆ market_na ┆ market_co ┆ market_ty ┆ group_typ │
        │ ---        ┆ ---        ┆ ---       ┆ ---    ┆   ┆ me        ┆ de        ┆ pe        ┆ e         │
        │ str        ┆ str        ┆ str       ┆ str    ┆   ┆ ---       ┆ ---       ┆ ---       ┆ ---       │
        │            ┆            ┆           ┆        ┆   ┆ str       ┆ i64       ┆ str       ┆ str       │
        ╞════════════╪════════════╪═══════════╪════════╪═══╪═══════════╪═══════════╪═══════════╪═══════════╡
        │ 7745894403 ┆ IRO1PNES00 ┆ IRO1PNES0 ┆ شپنا   ┆ … ┆ بازار     ┆ 1         ┆ بازار اول ┆ N1        │
        │ 636165     ┆ 01         ┆ 000       ┆        ┆   ┆ بورس      ┆           ┆ (تابلوی   ┆           │
        │            ┆            ┆           ┆        ┆   ┆           ┆           ┆ اصلی)     ┆           │
        │            ┆            ┆           ┆        ┆   ┆           ┆           ┆ بورس      ┆           │
        │ 6588383819 ┆ IRO1IKCO00 ┆ IRO1IKCO0 ┆ خودرو  ┆ … ┆ بازار     ┆ 1         ┆ بازار دوم ┆ N2        │
        │ 5688438    ┆ 01         ┆ 008       ┆        ┆   ┆ بورس      ┆           ┆ (تابلوی   ┆           │
        │            ┆            ┆           ┆        ┆   ┆           ┆           ┆ فرعی)     ┆           │
        │            ┆            ┆           ┆        ┆   ┆           ┆           ┆ بورس      ┆           │
        └────────────┴────────────┴───────────┴────────┴───┴───────────┴───────────┴───────────┴───────────┘

        >>> tsetmc.ins_info(symbol = ["شپنا", "خودرو"])
        shape: (2, 24)
        ┌────────────┬────────────┬───────────┬────────┬───┬───────────┬───────────┬───────────┬───────────┐
        │ ins_code   ┆ ins_id     ┆ isin      ┆ symbol ┆ … ┆ market_na ┆ market_co ┆ market_ty ┆ group_typ │
        │ ---        ┆ ---        ┆ ---       ┆ ---    ┆   ┆ me        ┆ de        ┆ pe        ┆ e         │
        │ str        ┆ str        ┆ str       ┆ str    ┆   ┆ ---       ┆ ---       ┆ ---       ┆ ---       │
        │            ┆            ┆           ┆        ┆   ┆ str       ┆ i64       ┆ str       ┆ str       │
        ╞════════════╪════════════╪═══════════╪════════╪═══╪═══════════╪═══════════╪═══════════╪═══════════╡
        │ 7745894403 ┆ IRO1PNES00 ┆ IRO1PNES0 ┆ شپنا   ┆ … ┆ بازار     ┆ 1         ┆ بازار اول ┆ N1        │
        │ 636165     ┆ 01         ┆ 000       ┆        ┆   ┆ بورس      ┆           ┆ (تابلوی   ┆           │
        │            ┆            ┆           ┆        ┆   ┆           ┆           ┆ اصلی)     ┆           │
        │            ┆            ┆           ┆        ┆   ┆           ┆           ┆ بورس      ┆           │
        │ 6588383819 ┆ IRO1IKCO00 ┆ IRO1IKCO0 ┆ خودرو  ┆ … ┆ بازار     ┆ 1         ┆ بازار دوم ┆ N2        │
        │ 5688438    ┆ 01         ┆ 008       ┆        ┆   ┆ بورس      ┆           ┆ (تابلوی   ┆           │
        │            ┆            ┆           ┆        ┆   ┆           ┆           ┆ فرعی)     ┆           │
        │            ┆            ┆           ┆        ┆   ┆           ┆           ┆ بورس      ┆           │
        └────────────┴────────────┴───────────┴────────┴───┴───────────┴───────────┴───────────┴───────────┘
        """

        ins_code = symbol if symbol else ins_code

        if isinstance(ins_code, str):
            ins_code = [ins_code]
        url = [self.url.ins_info(i) for i in ins_code]
        r = self.requests(url)
        records = [
            InsInfo.model_validate(i.get("instrumentInfo")).model_dump() for i in r
        ]
        df = pl.from_dicts(records)
        return df

    def specific_option_data(self, ins_id: str | list[str]) -> pl.DataFrame:
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
        ┌──────────────────┬───────────────────┬──────────────┬────────────┬──────────┬────────┬───────────────┐
        │ ins_code         ┆ ua_ins_code       ┆ begin_date   ┆ ex_date    ┆ lot_size ┆ k      ┆ open_interest │
        │ ---              ┆ ---               ┆ ---          ┆ ---        ┆ ---      ┆ ---    ┆ ---           │
        │ str              ┆ str               ┆ date         ┆ date       ┆ i64      ┆ f64    ┆ i64           │
        ╞══════════════════╪═══════════════════╪══════════════╪════════════╪══════════╪════════╪═══════════════╡
        │ 8907495648806531 ┆ 65883838195688438 ┆ 2023-09-30   ┆ 2024-02-21 ┆ 1000     ┆ 2600.0 ┆ 1006          │
        │ 4785638272776115 ┆ 65883838195688438 ┆ 2023-10-28   ┆ 2024-03-27 ┆ 1000     ┆ 3750.0 ┆ 0             │
        └──────────────────┴───────────────────┴──────────────┴────────────┴──────────┴────────┴───────────────┘
        """
        if isinstance(ins_id, str):
            ins_id = [ins_id]
        url = [self.url.specific_option_data(i) for i in ins_id]
        r = get(url)
        df = pl.from_records([i.get("instrumentOption") for i in r])
        df = manipulation_cols(df, columns=cols.tsetmc.specific_option_data)
        df = df.with_columns(
            [
                pl.col("listed_date").cast(pl.Utf8).str.to_date("%Y%m%d"),
                pl.col("ex_date").cast(pl.Utf8).str.to_date("%Y%m%d"),
            ]
        )
        return df

    @_handle_ins_cod_or_symbol
    def hist_price(
        self,
        symbol: str | list[str] | None = None,
        ins_code: str | list[str] | None = None,
        start: str | None = None,
        end: str | None = None,
    ) -> pl.DataFrame:
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
            کدِ صفحه‌یِ نماد

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
        r = get(url)
        df = pl.DataFrame()
        for resp in r:
            df_ = pl.DataFrame(
                [HistPrice.model_validate(i) for i in resp["closingPriceDaily"]]
            )
            df = pl.concat([df, df_])
        return df

    @_handle_ins_cod_or_symbol
    def adj_hist_price(
        self,
        symbol: str | list[str] | None = None,
        ins_code: str | list[str] | None = None,
        start: str | None = None,
        end: str | None = None,
    ) -> pl.DataFrame:
        """
        .. raw:: html

            <div dir="rtl">
                داده‌هایِ تاریخیِ مروبط به معامله‌یِ نماد رو استخراج  و به همراهِِ تعدیلی برمی‌گردونه.
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
            کدِ صفحه‌یِ نماد

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
            df.sort("date")
            .with_columns(
                factor=(pl.col("y_final").shift(-1) / pl.col("final"))
                .fill_null(1)
                .reverse()
                .cum_prod()
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

    @_handle_ins_cod_or_symbol
    def intraday_trades(
        self,
        symbol: str | list[str] | None = None,
        ins_code: str | list[str] | None = None,
    ) -> pl.DataFrame:
        """
        .. raw:: html

            <div dir="rtl">
                داده‌هایِ معامله‌یِ دورن-روزی(ریزِ معامله) رو برای آخرین روزِ معاملاتی استخراج و برمی‌گردونه.
            </div>

        Parameters
        ----------
        symbol: str | list[str] | None
            نماد
        ins_code: str | list[str] | None
            کدِ صفحه‌یِ نماد

        Returns
        -------
        polars.DataFrame

        example
        -------
        >>> from oxtapus import TSETMC
        >>> tsetmc = TSETMC()
        >>> tsetmc.intraday_trades("دکپسول")
        shape: (190, 4)
        ┌─────────────────────┬───────────┬─────────┬────────┐
        │ datetime            ┆ trade_nbr ┆ price   ┆ volume │
        │ ---                 ┆ ---       ┆ ---     ┆ ---    │
        │ datetime[μs]        ┆ i64       ┆ f64     ┆ i64    │
        ╞═════════════════════╪═══════════╪═════════╪════════╡
        │ 2023-11-01 09:10:01 ┆ 1         ┆ 75100.0 ┆ 250    │
        │ 2023-11-01 09:10:05 ┆ 2         ┆ 75100.0 ┆ 625    │
        │ 2023-11-01 09:10:05 ┆ 3         ┆ 75100.0 ┆ 48     │
        │ 2023-11-01 09:11:57 ┆ 4         ┆ 75150.0 ┆ 100    │
        │ …                   ┆ …         ┆ …       ┆ …      │
        │ 2023-11-01 12:28:47 ┆ 187       ┆ 77000.0 ┆ 510    │
        │ 2023-11-01 12:28:47 ┆ 188       ┆ 77000.0 ┆ 89     │
        │ 2023-11-01 12:29:06 ┆ 189       ┆ 77000.0 ┆ 411    │
        │ 2023-11-01 12:29:06 ┆ 190       ┆ 77000.0 ┆ 500    │
        └─────────────────────┴───────────┴─────────┴────────┘
        """
        ins_code = symbol if symbol else ins_code
        if isinstance(ins_code, str):
            ins_code = [ins_code]
        url = [self.url.intraday_trades(i) for i in ins_code]
        url_last_ins_data = [self.url.last_ins_data(i) for i in ins_code]
        r = get(url)
        last_ins_data = get(url_last_ins_data)
        df = pl.DataFrame()
        for i, record in enumerate(r):
            df_ = pl.from_dicts(record["trade"])
            df_ = df_.with_columns(
                date=pl.lit(last_ins_data[i]["closingPriceInfo"]["finalLastDate"])
            )
            df_ = df_.with_columns(
                pl.concat_str(
                    pl.col("date").cast(pl.Utf8),
                    pl.lit(" "),
                    pl.when(pl.col("hEven").cast(pl.Utf8).str.len_bytes() == 5)
                    .then(pl.concat_str(pl.lit("0"), pl.col("hEven").cast(pl.Utf8)))
                    .otherwise(pl.col("hEven").cast(pl.Utf8)),
                )
                .str.to_datetime(format="%Y%m%d %H%M%S")
                .alias("datetime")
            )
            df_ = manipulation_cols(df_, columns=cols.tsetmc.intraday_trades)
            df = pl.concat([df, df_])
        return df

    def intraday_trades_based_on_timeframe(
        self,
        symbol: str | list[str] | None = None,
        ins_code: str | list[str] | None = None,
        timeframe: str = "5m",
    ) -> pl.DataFrame:
        """
        .. raw:: html

            <div dir="rtl">
                داده‌هایِ معامله‌یِ دورن-روزی(ریزِ معامله) رو برای آخرین روزِ معاملاتی استخراج و
                بر مبنایِ تایم-فریمِ وارد شده باز-سازی می‌کنه و برمی‌گردونه.
            </div>

        Parameters
        ----------
        symbol: str | list[str] | None
            نماد
        ins_code: str | list[str] | None
            کدِ صفحه‌یِ نماد
        timeframe: str, {'1m', '5m', '1h', ...}, default '5m'
             فاصله‌یِ زمانی(تایم-فریم)
             `برای آگاهی‌ِ بیشتر این صفحه رو بخون <https://pola-rs.github.io/polars/py-polars/html/reference/dataframe/api/polars.DataFrame.group_by_dynamic.html>`__.

        Returns
        -------
        polars.DataFrame

        example
        -------
        >>> from oxtapus import TSETMC
        >>> tsetmc = TSETMC()
        >>> tsetmc.intraday_trades_based_on_timeframe("دکپسول")
        shape: (24, 7)
        ┌─────────────────────┬─────────┬─────────┬─────────┬─────────┬────────┬────────────┐
        │ datetime            ┆ open    ┆ high    ┆ low     ┆ close   ┆ volume ┆ value      │
        │ ---                 ┆ ---     ┆ ---     ┆ ---     ┆ ---     ┆ ---    ┆ ---        │
        │ datetime[μs]        ┆ f64     ┆ f64     ┆ f64     ┆ f64     ┆ i64    ┆ f64        │
        ╞═════════════════════╪═════════╪═════════╪═════════╪═════════╪════════╪════════════╡
        │ 2023-11-01 09:10:00 ┆ 75100.0 ┆ 75150.0 ┆ 75100.0 ┆ 75150.0 ┆ 2273   ┆ 1.707698e8 │
        │ 2023-11-01 09:15:00 ┆ 75200.0 ┆ 75200.0 ┆ 75200.0 ┆ 75200.0 ┆ 106    ┆ 7.9712e6   │
        │ 2023-11-01 09:25:00 ┆ 75300.0 ┆ 75300.0 ┆ 75000.0 ┆ 75250.0 ┆ 8821   ┆ 6.638115e8 │
        │ 2023-11-01 09:40:00 ┆ 76500.0 ┆ 76500.0 ┆ 75200.0 ┆ 75200.0 ┆ 4084   ┆ 3.078858e8 │
        │ …                   ┆ …       ┆ …       ┆ …       ┆ …       ┆ …      ┆ …          │
        │ 2023-11-01 12:10:00 ┆ 76500.0 ┆ 77350.0 ┆ 76500.0 ┆ 77350.0 ┆ 24590  ┆ 1.8976e9   │
        │ 2023-11-01 12:15:00 ┆ 77350.0 ┆ 77350.0 ┆ 77000.0 ┆ 77000.0 ┆ 6085   ┆ 4.699499e8 │
        │ 2023-11-01 12:20:00 ┆ 77000.0 ┆ 77350.0 ┆ 77000.0 ┆ 77350.0 ┆ 7660   ┆ 5.915905e8 │
        │ 2023-11-01 12:25:00 ┆ 77200.0 ┆ 77200.0 ┆ 77000.0 ┆ 77000.0 ┆ 2981   ┆ 2.29551e8  │
        └─────────────────────┴─────────┴─────────┴─────────┴─────────┴────────┴────────────┘
        """
        df = self.intraday_trades(symbol=symbol, ins_code=ins_code)
        df = (
            df.sort("datetime")
            .group_by_dynamic("datetime", every=timeframe)
            .agg(
                open=pl.col("price").first(),
                high=pl.col("price").max(),
                low=pl.col("price").min(),
                close=pl.col("price").last(),
                volume=pl.col("volume").sum(),
                value=(pl.col("price").mul(pl.col("volume"))).sum(),
            )
        )
        return df

    @_handle_ins_cod_or_symbol
    def last_ins_data(
        self,
        symbol: str | list[str] | None = None,
        ins_code: str | list[str] | None = None,
    ) -> pl.DataFrame:
        """
        .. raw:: html

            <div dir="rtl">
                داده‌هایِ صفحه‌یِ نماد رو استخراج و پالایش می‌کنه.
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
            کدِ صفحه‌یِ نماد

        Returns
        -------
        polars.DataFrame

        example
        -------
        >>> from oxtapus import TSETMC
        >>> tsetmc = TSETMC()
        >>> tsetmc.last_ins_data(symbol=["خودرو","خساپا"])
        shape: (2, 17)
        ┌────────────┬────────┬────────┬────────────┬───┬────────────┬────────────┬─────────┬─────────┐
        │ date       ┆ time   ┆ status ┆ status_far ┆ … ┆ event_date ┆ event_time ┆ i_close ┆ y_close │
        │ ---        ┆ ---    ┆ ---    ┆ ---        ┆   ┆ ---        ┆ ---        ┆ ---     ┆ ---     │
        │ date       ┆ i64    ┆ str    ┆ str        ┆   ┆ date       ┆ i64        ┆ bool    ┆ bool    │
        ╞════════════╪════════╪════════╪════════════╪═══╪════════════╪════════════╪═════════╪═════════╡
        │ 2023-11-01 ┆ 122959 ┆ A      ┆ مجاز       ┆ … ┆ 2023-11-01 ┆ 122959     ┆ false   ┆ false   │
        │ 2023-11-01 ┆ 122959 ┆ A      ┆ مجاز       ┆ … ┆ 2023-11-01 ┆ 122959     ┆ false   ┆ false   │
        └────────────┴────────┴────────┴────────────┴───┴────────────┴────────────┴─────────┴─────────┘
        """
        ins_code = symbol if symbol else ins_code
        if isinstance(ins_code, str):
            ins_code = [ins_code]
        url = [self.url.last_ins_data(i) for i in ins_code]
        r = get(url)
        dicts = [
            {
                **record.get("closingPriceInfo").pop("instrumentState"),
                **record.get("closingPriceInfo"),
            }
            for record in r
        ]
        df = pl.from_dicts(dicts)
        df = manipulation_cols(df, columns=cols.tsetmc.last_ins_data).with_columns(
            [
                pl.col("date").cast(pl.Utf8).str.to_date(format="%Y%m%d"),
                pl.col("event_date").cast(pl.Utf8).str.to_date(format="%Y%m%d"),
            ]
        )

        return df

    @_handle_ins_cod_or_symbol
    def client_type(
        self,
        symbol: str | list[str] | None = None,
        ins_code: str | list[str] | None = None,
    ) -> pl.DataFrame:
        """
        .. raw:: html

            <div dir="rtl">
                داده‌هایِ تاریخیِ مروبط به معامله‌هایِ حقیقی-حقوقی رو استخراج و پالایش می‌کنه.
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
            کدِ صفحه‌یِ نماد

        Returns
        -------
        polars.DataFrame

        example
        -------
        >>> from oxtapus import TSETMC
        >>> tsetmc = TSETMC()
        >>> tsetmc.client_type(symbol="خودرو")
        shape: (3_115, 14)
        ┌────────────┬───────────────────┬──────────────────┬───┬───────────────┬───────────────────┬───────────────────┐
        │ date       ┆ ins_code          ┆ vol_purchase_ind ┆ … ┆ val_sales_ins ┆ sellers_count_ins ┆ sellers_count_ind │
        │ ---        ┆ ---               ┆ ---              ┆   ┆ ---           ┆ ---               ┆ ---               │
        │ date       ┆ str               ┆ f64              ┆   ┆ f64           ┆ i64               ┆ i64               │
        ╞════════════╪═══════════════════╪══════════════════╪═══╪═══════════════╪═══════════════════╪═══════════════════╡
        │ 2008-11-26 ┆ 65883838195688438 ┆ 35092.0          ┆ … ┆ 1.54854651e8  ┆ 7                 ┆ 66                │
        │ 2008-11-29 ┆ 65883838195688438 ┆ 139905.0         ┆ … ┆ 2.62977529e8  ┆ 8                 ┆ 70                │
        │ 2008-11-30 ┆ 65883838195688438 ┆ 30471.0          ┆ … ┆ 1.85145104e8  ┆ 8                 ┆ 87                │
        │ 2008-12-01 ┆ 65883838195688438 ┆ 95608.0          ┆ … ┆ 1.50880556e8  ┆ 6                 ┆ 67                │
        │ …          ┆ …                 ┆ …                ┆ … ┆ …             ┆ …                 ┆ …                 │
        │ 2023-10-29 ┆ 65883838195688438 ┆ 2.42294804e8     ┆ … ┆ 1.3174e11     ┆ 16                ┆ 1746              │
        │ 2023-10-30 ┆ 65883838195688438 ┆ 1.8910082e8      ┆ … ┆ 3.7981e10     ┆ 11                ┆ 1912              │
        │ 2023-10-31 ┆ 65883838195688438 ┆ 1.04700395e8     ┆ … ┆ 5.9403e9      ┆ 3                 ┆ 1191              │
        │ 2023-11-01 ┆ 65883838195688438 ┆ 1.31498895e8     ┆ … ┆ 6.0731e10     ┆ 10                ┆ 1356              │
        └────────────┴───────────────────┴──────────────────┴───┴───────────────┴───────────────────┴───────────────────┘
        """
        ins_code = symbol if symbol else ins_code
        if isinstance(ins_code, str):
            ins_code = [ins_code]
        url = [self.url.client_type(i) for i in ins_code]
        r = self.requests(url)
        df = pl.DataFrame()
        for resp in r:
            df_ = pl.from_records(resp.get("clientType"), orient="col")
            df_ = (
                manipulation_cols(df_, columns=cols.tsetmc.client_type)
                .with_columns(pl.col("date").cast(pl.Utf8).str.to_date(format="%Y%m%d"))
                .sort("date")
            )
            df = pl.concat([df, df_])
        return df

    @_handle_ins_cod_or_symbol
    def share_change(
        self,
        symbol: str | list[str] | None = None,
        ins_code: str | list[str] | None = None,
    ) -> pl.DataFrame:
        """
        .. raw:: html

            <div dir="rtl">
                داده‌هایِ تاریخیِ مروبط به تغییرِ سرمایه رو استخراج و پالایش می‌کنه.
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
            کدِ صفحه‌یِ نماد

        Returns
        -------
        polars.DataFrame

        example
        -------
        >>> from oxtapus import TSETMC
        >>> tsetmc = TSETMC()
        >>> tsetmc.share_change(ins_code = "35425587644337450")
        shape: (10, 4)
        ┌────────────┬───────────────────┬───────────┬───────────┐
        │ date       ┆ ins_code          ┆ previous  ┆ current   │
        │ ---        ┆ ---               ┆ ---       ┆ ---       │
        │ date       ┆ str               ┆ f64       ┆ f64       │
        ╞════════════╪═══════════════════╪═══════════╪═══════════╡
        │ 2011-07-05 ┆ 35425587644337450 ┆ 5.7896e9  ┆ 1.7369e10 │
        │ 2013-06-10 ┆ 35425587644337450 ┆ 1.7369e10 ┆ 3.5000e10 │
        │ 2014-12-02 ┆ 35425587644337450 ┆ 3.5000e10 ┆ 4.3400e10 │
        │ 2016-07-19 ┆ 35425587644337450 ┆ 4.3400e10 ┆ 5.0000e10 │
        │ …          ┆ …                 ┆ …         ┆ …         │
        │ 2020-01-22 ┆ 35425587644337450 ┆ 7.8000e10 ┆ 1.0140e11 │
        │ 2020-12-06 ┆ 35425587644337450 ┆ 1.0140e11 ┆ 2.0000e11 │
        │ 2021-11-28 ┆ 35425587644337450 ┆ 2.0000e11 ┆ 4.0000e11 │
        │ 2023-03-15 ┆ 35425587644337450 ┆ 4.0000e11 ┆ 6.0000e11 │
        └────────────┴───────────────────┴───────────┴───────────┘
        """

        ins_code = symbol if symbol else ins_code
        if isinstance(ins_code, str):
            ins_code = [ins_code]
        url = [self.url.share_change(i) for i in ins_code]
        r = self.requests(url)
        df = pl.DataFrame()
        for resp in r:
            df_ = pl.from_records(resp.get("instrumentShareChange"), orient="col")
            df_ = (
                manipulation_cols(df_, columns=cols.tsetmc.share_change)
                .with_columns(pl.col("date").cast(pl.Utf8).str.to_date(format="%Y%m%d"))
                .sort("date")
            )
            df = pl.concat([df, df_])

        return df

    def indexes(self):
        """
        .. raw:: html

            <div dir="rtl">
                لیستِ همه‌یِ شاخص‌ها و مقدار و تغییرِ مربوط به آخرین روزِ معاملاتی رو استخراج و پالایش می‌کنه.
            </div>

        Returns
        -------
        polars.DataFrame

        example
        -------
        >>> from oxtapus import TSETMC
        >>> tsetmc = TSETMC()
        >>> tsetmc.indexes()
        """
        r = get(self.url.indexes())[0].get("indexB1")
        df = pl.from_records(r)
        df = manipulation_cols(df, columns=cols.tsetmc.indexes)
        return df

    def symbols_that_index_tracks(self, ind_code: str | list[str]):
        """
        .. raw:: html

            <div dir="rtl">
                نمادهایی که هر شاخص دنبال می‌کنه رو استخراج و پالایش می‌کنه.
            </div>

        Parameters
        ---------
        ind_code: str or list[str]
            کدِ صفحه‌یِ شاخص

        Returns
        -------
        polars.DataFrame

        example
        -------
        >>> from oxtapus import TSETMC
        >>> tsetmc = TSETMC()
        >>> tsetmc.symbols_that_index_tracks(["21948907150049163", "3615666621538524"])
        shape: (39, 3)
        ┌───────────────────┬───────────────────┬────────┐
        │ ind_code          ┆ ins_code          ┆ symbol │
        │ ---               ┆ ---               ┆ ---    │
        │ str               ┆ str               ┆ str    │
        ╞═══════════════════╪═══════════════════╪════════╡
        │ 21948907150049163 ┆ 67030488744129337 ┆ قپيرا  │
        │ 21948907150049163 ┆ 44967158778304588 ┆ قثابت  │
        │ 21948907150049163 ┆ 15259343650667588 ┆ قزوين  │
        │ 21948907150049163 ┆ 35964395659427029 ┆ قشكر   │
        │ …                 ┆ …                 ┆ …      │
        │ 3615666621538524  ┆ 69090868458637360 ┆ ديران  │
        │ 3615666621538524  ┆ 36899214178084525 ┆ شفا    │
        │ 3615666621538524  ┆ 57944184894703821 ┆ والبر  │
        │ 3615666621538524  ┆ 7183333492448248  ┆ وپخش   │
        └───────────────────┴───────────────────┴────────┘
        """
        if isinstance(ind_code, str):
            ind_code = [ind_code]
        url = [self.url.symbols_that_index_tracks(i) for i in ind_code]
        r = self.requests(url)
        df = pl.DataFrame()
        for i, resp in enumerate(r):
            records = [
                {
                    "ind_code": ind_code[i],
                    "ins_code": ins["instrument"]["insCode"],
                    "symbol": ins["instrument"]["lVal18AFC"],
                }
                for ins in resp["indexCompany"]
            ]
            df_ = pl.from_records(records, orient="col")
            df = pl.concat([df, df_])
        return df

    def index_hist(self, ind_code: str | list[str]):
        """
        .. raw:: html

            <div dir="rtl">
                داده‌هایِ تاریخیِ مربوط به شاخص‌ها رو استخراج و پالایش می‌کنه.
            </div>

        Parameters
        ---------
        ind_code: str or list[str]
            کدِ صفحه‌یِ شاخص

        Returns
        -------
        polars.DataFrame

        example
        -------
        >>> from oxtapus import TSETMC
        >>> tsetmc = TSETMC()
        >>> tsetmc.index_hist(["21948907150049163", "3615666621538524"])
        shape: (7_195, 5)
        ┌────────────┬───────────────────┬──────────┬──────────┬──────────┐
        │ date       ┆ ind_code          ┆ close    ┆ low      ┆ high     │
        │ ---        ┆ ---               ┆ ---      ┆ ---      ┆ ---      │
        │ date       ┆ i64               ┆ f64      ┆ f64      ┆ f64      │
        ╞════════════╪═══════════════════╪══════════╪══════════╪══════════╡
        │ 2008-12-05 ┆ 21948907150049163 ┆ 347.0    ┆ 347.0    ┆ 347.0    │
        │ 2008-12-06 ┆ 21948907150049163 ┆ 347.0    ┆ 347.0    ┆ 347.0    │
        │ 2008-12-07 ┆ 21948907150049163 ┆ 345.5    ┆ 345.5    ┆ 347.1    │
        │ 2008-12-08 ┆ 21948907150049163 ┆ 345.6    ┆ 345.6    ┆ 345.6    │
        │ …          ┆ …                 ┆ …        ┆ …        ┆ …        │
        │ 2023-10-29 ┆ 3615666621538524  ┆ 183906.0 ┆ 183587.0 ┆ 183990.0 │
        │ 2023-10-30 ┆ 3615666621538524  ┆ 184755.0 ┆ 183950.0 ┆ 184755.0 │
        │ 2023-10-31 ┆ 3615666621538524  ┆ 184465.0 ┆ 184465.0 ┆ 184756.0 │
        │ 2023-11-01 ┆ 3615666621538524  ┆ 184405.0 ┆ 184359.0 ┆ 184622.0 │
        └────────────┴───────────────────┴──────────┴──────────┴──────────┘
        """
        if isinstance(ind_code, str):
            ind_code = [ind_code]
        url = [self.url.index_hist(i) for i in ind_code]
        r = self.requests(url)
        df = pl.DataFrame()
        for resp in r:
            df_ = pl.from_records(resp["indexB2"], orient="col")
            df_ = (
                manipulation_cols(df_, columns=cols.tsetmc.index_hist)
                .with_columns(pl.col("date").cast(pl.Utf8).str.to_date(format="%Y%m%d"))
                .sort("date")
            )
            df = pl.concat([df, df_])
        return df

    def last_market_activity_datetime(self):
        """
        .. raw:: html

            <div dir="rtl">
                تاریخ و زمانِ رو بر مبنایِ آخرین رویدادِ بازار برمی‌گردونه.
            </div>

        Returns
        -------
        datetime.datetime

        example
        -------
        >>> from datetime import datetime
        >>> from oxtapus import TSETMC
        >>> datetime.now()
        datetime.datetime(2023, 11, 3, 20, 7, 36, 378137)
        >>> TSETMC().last_market_activity_datetime()
        datetime.datetime(2023, 11, 1, 19, 21, 24)
        """
        r = get(self.url.last_market_activity())[0].get("marketOverview")
        date = r.get("marketActivityDEven")
        time = r.get("marketActivityHEven")
        return datetime.datetime.strptime(f"{date} {time}", "%Y%m%d %H%M%S")

    @_handle_ins_cod_or_symbol
    def shareholder_list(
        self,
        symbol: str | list[str] | None = None,
        ins_code: str | list[str] | None = None,
    ) -> pl.DataFrame:
        """
        .. raw:: html

            <div dir="rtl">
                داده‌هایِ مربوط به سهامدارهایِ عمده رو استخراج و پالایش می‌کنه.
            </div>

        Parameters
        ---------
        symbol: str | list[str] | None
            نماد
        ins_code: str | list[str] | None
            کدِ صفحه‌یِ نماد

        Returns
        -------
        polars.DataFrame

        example
        -------
        >>> from oxtapus import TSETMC
        >>> tsetmc = TSETMC()
        >>> tsetmc.shareholder_list(ins_code=["71483646978964608"])
        shape: (3, 6)
        ┌──────────────┬───────────────────────────────────┬──────────────┬────────────┬────────┬───────────────┐
        │ ins_id       ┆ sh_name                           ┆ shares       ┆ pct_shares ┆ change ┆ change_amount │
        │ ---          ┆ ---                               ┆ ---          ┆ ---        ┆ ---    ┆ ---           │
        │ str          ┆ str                               ┆ f64          ┆ f64        ┆ i64    ┆ f64           │
        ╞══════════════╪═══════════════════════════════════╪══════════════╪════════════╪════════╪═══════════════╡
        │ IRO1ZOBI0002 ┆ سازمان تامين اجتماعي              ┆ 3.9592e10    ┆ 55.93      ┆ 1      ┆ 0.0           │
        │ IRO1ZOBI0002 ┆ شركت پويش بازرگان ذوب آهن اصفهان… ┆ 1.2217e10    ┆ 17.26      ┆ 1      ┆ 0.0           │
        │ IRO1ZOBI0002 ┆ شركت سرمايه گذاري سامان فرهنگيان… ┆ 8.36525894e8 ┆ 1.18       ┆ 1      ┆ 0.0           │
        └──────────────┴───────────────────────────────────┴──────────────┴────────────┴────────┴───────────────┘
        """
        ins_code = symbol if symbol else ins_code
        if isinstance(ins_code, str):
            ins_code = [ins_code]
        url = [self.url.shareholder_list(i) for i in ins_code]
        r = self.requests(url)
        df = pl.DataFrame()
        for resp in r:
            df_ = pl.from_dicts(resp.get("shareHolder"))
            df_ = manipulation_cols(df_, columns=cols.tsetmc.shareholder_list)
            df = pl.concat([df, df_])
        return df

    def adjust_price_flow(self, last_records: int):
        """
        .. raw:: html

            <div dir="rtl">
                قیمتِ تعدیلی و قبلِ تعدیل نمادهایی که قیمتشون تعدیل شده رو بهت می‌ده.
            </div>

        Parameters
        ---------
        last_records: str | list[str] | None
            تعدادِ آخرین رکوردهایی که می‌خوای از هر بازارِ بورس و فرابورس بگیری

        Returns
        -------
        polars.DataFrame

        example
        -------
        >>> from oxtapus import TSETMC
        >>> tsetmc = TSETMC()
        >>> tsetmc.adjust_price_flow(2)
        shape: (4, 5)
        ┌───────────────────┬────────┬────────────┬───────────┬─────────┐
        │ ins_code          ┆ symbol ┆ date       ┆ adj_final ┆ final   │
        │ ---               ┆ ---    ┆ ---        ┆ ---       ┆ ---     │
        │ str               ┆ str    ┆ date       ┆ f64       ┆ f64     │
        ╞═══════════════════╪════════╪════════════╪═══════════╪═════════╡
        │ 27405735172634593 ┆ اتكام  ┆ 2024-01-22 ┆ 4262.0    ┆ 4842.0  │
        │ 30852391633490755 ┆ ثفارس  ┆ 2024-01-22 ┆ 45820.0   ┆ 45984.0 │
        │ 55862580907068610 ┆ شملي   ┆ 2024-01-21 ┆ 8090.0    ┆ 8630.0  │
        │ 21096748051392414 ┆ سغدير  ┆ 2024-01-20 ┆ 8900.0    ┆ 10090.0 │
        └───────────────────┴────────┴────────────┴───────────┴─────────┘
        """
        r_tse = get(self.url.tse_adjust_price_flow(last_records))
        r_ifb = get(self.url.ifb_adjust_price_flow(last_records))
        nnd = normalize_nested_dict(
            [*r_tse[0]["priceAdjust"], *r_ifb[0]["priceAdjust"]], "instrument"
        )
        df = pl.from_dicts([AdjustPriceFlow(**i).model_dump() for i in nnd])
        return df

    def ins_share_change_flow(self):
        """
        .. raw:: html

            <div dir="rtl">
                افزایش/تغییرِ سرمایه‌یِ همه‌یِ شرکت‌ها رو بهت می‌ده.
            </div>

        Returns
        -------
        polars.DataFrame

        example
        -------
        >>> from oxtapus import TSETMC
        >>> tsetmc = TSETMC()
        >>> tsetmc.ins_share_change_flow()
        shape: (2_639, 5)
        ┌───────────────────┬──────────────┬────────────┬────────────────┬─────────────────┐
        │ ins_code          ┆ symbol       ┆ date       ┆ current_shares ┆ previous_shares │
        │ ---               ┆ ---          ┆ ---        ┆ ---            ┆ ---             │
        │ str               ┆ str          ┆ date       ┆ i64            ┆ i64             │
        ╞═══════════════════╪══════════════╪════════════╪════════════════╪═════════════════╡
        │ 30852391633490755 ┆ ثفارس        ┆ 2024-01-24 ┆ 4050000000     ┆ 1800000000      │
        │ 27405735172634593 ┆ اتكام        ┆ 2024-01-24 ┆ 12400000000    ┆ 8000000000      │
        │ 30852391633490755 ┆ ثفارس        ┆ 2024-01-22 ┆ 1800000000     ┆ 4050000000      │
        │ 27405735172634593 ┆ اتكام        ┆ 2024-01-22 ┆ 8000000000     ┆ 12400000000     │
        │ 19471788163911687 ┆ كفپارس       ┆ 2024-01-21 ┆ 2500000000     ┆ 1619519000      │
        │ …                 ┆ …            ┆ …          ┆ …              ┆ …               │
        │ 48287330843249460 ┆ كارآفريني    ┆ 2010-09-28 ┆ 648000000      ┆ 23300000        │
        │ 35113075091643530 ┆ پترو گچساران ┆ 2010-09-28 ┆ 259700000      ┆ 100000          │
        │ 9109623461944634  ┆ فريم         ┆ 2010-08-30 ┆ 615256         ┆ 196000000       │
        │ 28520500657715290 ┆ نكا          ┆ 2010-08-30 ┆ 1781550        ┆ 4900000         │
        │ 57857218314224912 ┆ پذيره-ستون   ┆ 2010-08-30 ┆ 350000000      ┆ 4900000         │
        └───────────────────┴──────────────┴────────────┴────────────────┴─────────────────┘
        """
        r_tse = get(self.url.tse_share_change_flow())
        r_ifb = get(self.url.ifb_share_change_flow())
        records = [
            *r_tse[0]["instrumentShareChange"],
            *r_ifb[0]["instrumentShareChange"],
        ]
        df = pl.from_dicts([InsShareChangeFlow(**i).model_dump() for i in records])
        return df
