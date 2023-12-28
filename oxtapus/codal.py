from typing import Literal, ClassVar
from urllib.parse import urlencode
from pydantic import BaseModel, ConfigDict, field_serializer
import polars as pl
from tarix import Date
from oxtapus.utils.http import requests, async_requests


def norm_char(w: str):
    dict_ = {
        "ي": "ی",
        "ك": "ک",
        "\u200c": "",
        "۰": "0",
        "۱": "1",
        "۲": "2",
        "۳": "3",
        "۴": "4",
        "۵": "5",
        "۶": "6",
        "۷": "7",
        "۸": "8",
        "۹": "9",
        "/": "-"
    }
    return w.translate(str.maketrans(dict_))


def jalali_to_gregorian(dtstr: str):
    """1402-05-12 12:20:42"""
    date = Date(dtstr[:10]).jalali_to_gregorian().strftime("%Y-%m-%d")
    time = dtstr[-8:]
    return f"{date} {time}"


def to_camel(string: str) -> str:
    return ''.join(word.capitalize() for word in string.split('_'))


class QueryParam(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    symbol: str
    category: Literal[1] = 1  # گروه اطلاعیه --> اطلاعات و صورت مالی سالانه
    publisher_type: Literal[1] = 1  # نوع شرکت --> ناشران
    letter_type: Literal[6] = 6  # نوع اطلاعیه --> اطلاعات و صورتهای مالی میاندوره ای
    length: Literal[3, 6, 9, 12]  # طول دوره
    audited: bool = True  # حسابرسی شده
    not_audited: bool = True  # حسابرسی نشده
    mains: bool = True  # فقط شرکت اصلی
    childs: bool = False  # فقط زیر-مجموعه‌ها
    consolidatable: bool = True  # اصلی
    not_consolidatable: bool = True  # تلفیقی

    auditor_ref: Literal[-1] = -1
    company_state: Literal[1] = 1
    Company_type: Literal[1] = 1
    page_number: int = 1
    tracing_no: Literal[-1] = -1
    publisher: bool = False
    is_not_audited: bool = False
    from_date: str = "1394/01/01"

    @field_serializer('audited', 'not_audited', 'mains', 'childs', 'consolidatable', 'not_consolidatable', 'publisher',
                      'is_not_audited')
    def serialize_bool(self, v: bool):
        return str(v).lower()


class Letters(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    base_url: ClassVar[str]

    tracing_no: int
    symbol: str
    company_name: str
    title: str
    letter_code: str
    sent_date_time: str
    publish_date_time: str
    has_html: bool
    is_estimate: bool
    has_excel: bool
    has_pdf: bool
    has_xbrl: bool
    has_attachment: bool
    url: str
    attachment_url: str
    pdf_url: str
    excel_url: str
    xbrl_url: str

    @field_serializer('symbol', 'company_name', "letter_code", "title")
    def serialize_norm_char(self, v: str):
        return norm_char(v)

    @field_serializer('sent_date_time', 'publish_date_time')
    def serialize_datetime(self, v: str):
        return jalali_to_gregorian(norm_char(v))

    @field_serializer('url', "attachment_url", "pdf_url")
    def serialize_url(self, v: str):
        if v:
            if v[0] != "/":
                v = f"/{v}"
            return f"{self.base_url}{v}"


class Codal:
    def __init__(self, query: QueryParam) -> None:
        self.base_url = "https://codal.ir"
        self.search_url = "https://search.codal.ir/api/search/v2/q?"
        self.api = "api/search/v2/q"
        self._query = query

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value: QueryParam):
        self._query = value

    def letter(self) -> pl.DataFrame:
        url = f"{self.search_url}{urlencode(self._query.model_dump(by_alias=True))}"
        r = requests(url)[0]
        pages = int(r.get("Page"))
        Letters.base_url = self.base_url
        letter_dicts = [Letters(**i).model_dump() for i in r["Letters"]]
        if pages > 1:
            for p in range(2, pages + 1):
                self._query.page_number = p
                url = f"{self.search_url}{urlencode(self._query.model_dump(by_alias=True))}"
                r = requests(url)[0]
                letter_dicts.extend([Letters(**i).model_dump() for i in r["Letters"]])

        return pl.from_dicts(letter_dicts)
