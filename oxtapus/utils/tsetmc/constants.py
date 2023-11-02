from typing import List
from urllib.parse import urlencode


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

    def option_info_comp(self, ins_id):
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
