from urllib.parse import urlencode


class URL:
    def __init__(self, base_url="http://cdn.tsetmc.com/api"):
        self.base_url = base_url

    def mw(
        self,
        stock: bool = False,
        ifb_paye: bool = False,
        mortgage: bool = False,
        cum_right: bool = False,
        bond: bool = False,
        option: bool = False,
        futures: bool = False,
        etf: bool = False,
        commodity: bool = False,
    ):
        """
        ترتیبَ ورودی‌ها مهم است، پس دقت کن!
        :param stock: bool, if True add stock data, default is False
        :param ifb_paye: bool, if True add ifb_pay data, default is False (فرابورس-پایه)
        :param mortgage: bool, if True add mortgage data, default is False
        :param cum_right: bool, if True add cum_right data, default is False
        :param bond: bool, if True add bond data, default is False
        :param option: bool, if True add option data, default is False
        :param futures: bool, if True add futures data, default is False
        :param etf: bool, if True add etf data, default is False
        :param commodity: bool, if True add commodity data, default is False
        :return: pandas.DataFrame
        """
        locals_ = locals()
        locals_.pop("self")
        l_kwargs = {key: val for key, val in locals_.items() if val}

        def paper_type():
            paper_type_ = {
                "stock": 1,
                "ifb_paye": 2,
                "mortgage": 3,
                "cum_right": 4,
                "bond": 5,
                "option": 6,
                "futures": 7,
                "etf": 8,
                "commodity": 9,
            }
            return {
                f"paperTypes[{i}]": paper_type_.get(k)
                for i, k in enumerate(l_kwargs.keys())
            }

        param = {
            "market": 0,
            "industrialGroup": "",
            **paper_type(),
            "showTraded": "false",
            "withBestLimits": "true",
        }
        return f"{self.base_url}/ClosingPrice/GetMarketWatch?{urlencode(param)}"

    def search_ins_code(self, symbol_far):
        return f"{self.base_url}/Instrument/getinstrumentsearch/{symbol_far}"

    def ins_info(self, ins_code):
        return f"{self.base_url}/Instrument/GetInstrumentInfo/{ins_code}"

    def hist_price(self, ins_code):
        return f"{self.base_url}/ClosingPrice/GetClosingPriceDailyList/{ins_code}/0"

    def client_type(self, ins_code):
        f"{self.base_url}/ClientType/GetClientTypeHistory/{ins_code}"

    def share_change(self, ins_code):
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
