import requests
import polars as pl

from oxtapus.models.rahavard import BalanceSheet
# from oxtapus.utils.http import requests

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
}

class Url:
    def __init__(self):
        self.base_url = "https://rahavard365.com/api/v2"

    def balance_sheet(self, ins_code):
        return f"{self.base_url}/asset/{ins_code}/balancesheets?_skip=0&_count=5&announcement_type_id=1"


class Rahavard:
    def __init__(self):
        self.url = Url()

    def balance_sheet(self):
        r = requests.get(self.url.balance_sheet("462"), headers=headers).json()
        d = BalanceSheet.model_validate(r)
        df = pl.DataFrame()
        field_info = pl.DataFrame()
        for bs in d.data:
            base = pl.from_dicts(
                [{**i.field.model_dump(), "value": i.value, "date": bs.date, "fiscal_year": bs.fiscal_year} for i in
                 bs.items])
            bsi = base.select(["date", "fiscal_year", "account", "value"])
            df = pl.concat([df, bsi])

            f_info = base.select(
                [
                    "title",
                    "english_title",
                    "account",
                    "is_parent",
                    "parent",
                    "index_view",
                    "id",
                    "sign_neg",
                    "sign_pos",
                    "neg_nature"
                ]
            )
            field_info = pl.concat([field_info, f_info])
        df = df.pivot(columns="account", values="value", index=["date", "fiscal_year"]).fill_null(0)
        base_info = {"announcement_type": d.data[0].announcement_type,
                     "financial_view_type": d.data[0].financial_view_type.id}
        field_info = field_info.unique(subset="index_view")
        return df, base_info, field_info
