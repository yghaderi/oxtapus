import pandas as pd

from .codal_utils import URL, QueryParameters, ced, cols
from ..utils import get


class Codal(URL):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def letters(self):
        main = get(self.search_url, verify=True, timeout=(2, 7)).json()
        df = pd.DataFrame(main.get("Letters")).rename(columns=cols.letters.rename)[
            cols.letters.rep
        ]
        page = main.get("Page")
        if page > 1:
            for i in range(1, page + 1):
                self.page_number = i
                main_ = get(self.search_url).json()
                df_ = pd.DataFrame(main_.get("Letters")).rename(
                    columns=cols.letters.rename
                )[cols.letters.rep]
                df = pd.concat([df, df_])
        df.replace({"\u200c": " "}, regex=True)
        return df

    def income_statements(self):
        letters = self.letters()
        df = pd.DataFrame()
        for i, row in letters.iterrows():
            url = self.financial_statements(letter_url=row.url, sheet_id=1)
            try:
                r = get(url, verify=True, timeout=(2, 10))
                df_ = ced.income_statements(r.text)
                df_ = df_.join(
                    pd.DataFrame.from_dict(
                        [
                            row[
                                [
                                    "symbol",
                                    "company_name",
                                    "title",
                                    "issue_datetime",
                                    "url",
                                ]
                            ].to_dict()
                        ]
                    )
                )
                df = pd.concat([df, df_])
            except Exception as e:
                print(e)
                print(url)

        return df[cols.income_statements.rep]

    def balance_sheet(self):
        letters = self.letters()
        df = pd.DataFrame()
        for i, row in letters.iterrows():
            url = self.financial_statements(letter_url=row.url, sheet_id=0)
            try:
                r = get(url, verify=True, timeout=(2, 10))
                df_ = ced.balance_sheet(r.text)
                df_ = df_.join(
                    pd.DataFrame.from_dict(
                        [
                            row[
                                [
                                    "symbol",
                                    "company_name",
                                    "title",
                                    "issue_datetime",
                                    "url",
                                ]
                            ].to_dict()
                        ]
                    )
                )
                df = pd.concat([df, df_])
            except Exception as e:
                print(e)
                print(url)
        return df[cols.balance_sheet.rep]
