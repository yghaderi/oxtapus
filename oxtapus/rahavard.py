import requests
import datetime as dt
import polars as pl
from dataclasses import dataclass

from oxtapus.models.rahavard import Stocks, BalanceSheet, IncomeStatements

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
}


def handel_clos(s: str):
    replace_dict = {" ": "_", "(": "", ")": "", ",": ""}
    return s.lower().translate(str.maketrans(replace_dict))


@dataclass
class BaseInfo:
    announcement_type: str
    financial_view_type: str


@dataclass
class Rep:
    data: pl.DataFrame
    base_info: BaseInfo
    field_info: pl.DataFrame


class Url:
    def __init__(self):
        self.base_url = "https://rahavard365.com/api/v2"

    def stocks(self) -> str:
        return f"{self.base_url}/market-data/stocks?last_trade=last_trading_day"

    def balance_sheet(self, ins_id, quarterly: bool) -> str:
        announcement_type_id = 1
        if quarterly:
            announcement_type_id = 3
        return f"{self.base_url}/asset/{ins_id}/balancesheets?_skip=0&_count=5&announcement_type_id={announcement_type_id}"

    def income_statements(self, ins_id, quarterly: bool) -> str:
        announcement_type_id = 1
        if quarterly:
            announcement_type_id = 3
        return f"{self.base_url}/asset/{ins_id}/profitloss?_skip=0&_count=3&announcement_type_id={announcement_type_id}"

    def cash_flow(self, ins_id) -> str:
        return f"{self.base_url}/asset/{ins_id}/cashflow?_skip=0&_count=5"


class Rahavard:
    def __init__(self):
        self.url = Url()
        self.last_get_stocks = None

    def stocks(self):
        r = requests.get(self.url.stocks(), headers=headers).json()
        d = Stocks.model_validate(r)
        self.stocks_: Stocks = d
        self.last_get_stocks = dt.datetime.now()
        return self

    def handle_get_stock(self):
        if not self.last_get_stocks:
            self.stocks()
        elif self.last_get_stocks < dt.datetime.now() - dt.timedelta(minutes=60):
            self.stocks()

    def balance_sheet(self, symbol: str, quarterly: bool = False):
        """ """
        self.handle_get_stock()
        ins_id = [i for i in self.stocks_.data if i.name == symbol][0]
        r = requests.get(
            self.url.balance_sheet(ins_id.asset_id, quarterly), headers=headers
        ).json()
        d = BalanceSheet.model_validate(r)
        df = pl.DataFrame()
        field_info = pl.DataFrame()
        for bs in d.data:
            base = pl.from_dicts(
                [
                    {
                        **i.field.model_dump(),
                        "value": i.value,
                        "date": bs.date,
                        "fiscal_year": bs.fiscal_year,
                    }
                    for i in bs.items
                ]
            )
            bsi = base.select(["date", "fiscal_year", "id", "value"])
            df = pl.concat([df, bsi])

            f_info = base.select(
                [
                    "id",
                    "title",
                    "english_title",
                    "account",
                    "is_parent",
                    "parent",
                    "index_view",
                    "sign_neg",
                    "sign_pos",
                    "neg_nature",
                ]
            )
            field_info = pl.concat([field_info, f_info])
        df = df.pivot(
            columns="id", values="value", index=["date", "fiscal_year"],
        ).fill_null(0)
        base_info = BaseInfo(
            announcement_type=d.data[0].announcement_type,
            financial_view_type=d.data[0].financial_view_type.id
        )
        field_info = field_info.unique(subset="id")
        return Rep(data=df, base_info=base_info, field_info=field_info)

    def income_statements(self, symbol: str, quarterly: bool = False):
        """ """
        self.handle_get_stock()
        ins_id = [i for i in self.stocks_.data if i.name == symbol][0]
        r = requests.get(
            self.url.income_statements(ins_id.asset_id, quarterly), headers=headers
        ).json()
        d = IncomeStatements.model_validate(r)
        df = pl.DataFrame()
        field_info = pl.DataFrame()
        for bs in d.data:
            base = pl.from_dicts(
                [
                    {
                        **i.field.model_dump(),
                        "value": i.value,
                        "date": bs.date,
                        "fiscal_year": bs.fiscal_year,
                    }
                    for i in bs.items
                ]
            )
            bsi = base.select(["date", "fiscal_year", "id", "value"])
            df = pl.concat([df, bsi])

            f_info = base.select(
                [
                    "id",
                    "title",
                    "english_title",
                    "account",
                    "is_parent",
                    "parent",
                    "index_view",
                    "sign_neg",
                    "sign_pos",
                    "neg_nature",
                ]
            )
            field_info = pl.concat([field_info, f_info])
        df = df.pivot(
            columns="id", values="value", index=["date", "fiscal_year"]
        ).fill_null(0)
        df.columns = list(map(lambda x: handel_clos(x), df.columns))
        base_info = BaseInfo(
            announcement_type=d.data[0].announcement_type_id,
            financial_view_type=d.data[0].financial_view_type_id
        )
        field_info = field_info.unique(subset="id")
        return Rep(data=df, base_info=base_info, field_info=field_info)
