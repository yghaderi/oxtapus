import pandas as pd
from .rahavard_utils import URL, ced
from ..utils import get


class Rahavard:
    def __init__(self):
        self.url = URL()
        self.symbol_id_ = self.symbol_id()

    def stock(self):
        t = get(self.url.stock(), verify=None).text
        return ced.parser(t)

    def symbol_id(self):
        df = pd.json_normalize(self.stock()["asset_data_list"])[
            ["asset.trade_symbol", "asset.id"]
        ]
        df.set_index("asset.trade_symbol", inplace=True)
        return df.to_dict()["asset.id"]

    def balance_sheet(self, symbol_far):
        t = get(
            self.url.balance_sheet(symbol_id=self.symbol_id_.get(symbol_far)),
            verify=None,
        ).text
        return ced.balance_sheet(t)

    def income_statements(self, symbol_far):
        t = get(
            self.url.income_statements(symbol_id=self.symbol_id_.get(symbol_far)),
            verify=None,
        ).text
        return ced.income_statements(t)

    def cash_flow(self, symbol_far):
        t = get(
            self.url.cash_flow(symbol_id=self.symbol_id_.get(symbol_far)), verify=None
        ).text
        return ced.cash_flow(t)
