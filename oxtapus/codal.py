import polars as pl
from typing import Literal
from pydantic import (
    validate_call,
)

from urllib.parse import urlencode
import re

from oxtapus.utils.codal.models import QueryParam, Letter, ErrorLog
from oxtapus.utils.codal.clean_data import HandleIncomeStatement
from oxtapus.utils.codal.request import request

Category = Literal["p", "i", "b"]


class Codal:
    @validate_call
    def __init__(self, query: QueryParam, category: Category) -> None:
        self.base_url = "https://codal.ir"
        self.search_url = "https://search.codal.ir/api/search/v2/q?"
        self.api = "api/search/v2/q"
        self._query = query
        self._category = category

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value: QueryParam):
        self._query = value

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value: Category):
        self._category = value

    def letter(self) -> pl.DataFrame:
        url = f"{self.search_url}{urlencode(self._query.model_dump(by_alias=True))}"
        r = request(url)[0]
        pages = int(r.get("Page"))
        Letter.base_url = self.base_url
        letter_dicts = [Letter(**i).model_dump() for i in r["Letters"]]
        if pages > 1:
            for p in range(2, pages + 1):
                self._query.page_number = p
                url = f"{self.search_url}{urlencode(self._query.model_dump(by_alias=True))}"
                r = request(url)[0]
                letter_dicts.extend([Letter(**i).model_dump() for i in r["Letters"]])

        return pl.from_dicts(letter_dicts)

    def _get_income_statements(self):
        url = [f"{i}&sheetId=1" for i in self.letter()["url"].to_list()]
        r = request(url=url, response="text")
        return r, url

    def income_statements(self, r):
        url = [f"{i}&sheetId=1" for i in self.letter()["url"].to_list()]
        # r = request(url=url, response="text")
        # r = self._get_income_statements()

        json_list = []
        find_data_log = []
        for i, text in enumerate(r):
            try:
                json_list.append(
                    re.findall("var.datasource.=(.*)", text)[0].split(";\r")[0]
                )
            except IndexError as e:
                find_data_log.append(
                    ("در این صفحه داده هایِ صورتِ سود(زیان) رو پیدا نکردم.", url[i], e)
                )

        df, validate_json_log = HandleIncomeStatement(
            category=self.category, json_list=json_list
        ).income_statements()
        error_log = ErrorLog(find_data=find_data_log, validate_json=validate_json_log)
        return df, error_log
