from typing import Literal, ClassVar, List, Tuple
import re
from urllib.parse import urlencode
from pydantic import BaseModel, ConfigDict, field_serializer, ValidationError
import polars as pl
from tarix import Date
import requests

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
}


def request(url: str | List[str], response: str = "json", timeout=(1, 10)):
    with requests.Session() as s:
        if isinstance(url, list):
            list_r = []
            for i in url:
                r = s.get(url=i, headers=headers, timeout=timeout)
                match response:
                    case "json":
                        list_r.append(r.json())
                    case "text":
                        list_r.append(r.text)
                    case _:
                        list_r.append(r)
            return list_r

        r = s.get(url=url, headers=headers, timeout=timeout)
        match response:
            case "json":
                return [r.json()]
            case "text":
                return [r.text]
            case _:
                return [r]


def norm_char(w: str):
    dict_ = {
        "ي": "ی",
        "ك": "ک",
        "\u200c": " ",
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
        "/": "-",
    }
    return w.translate(str.maketrans(dict_))


def jalali_to_gregorian(dtstr: str):
    """1402-05-12 12:20:42"""
    date = Date(dtstr[:10]).jalali_to_gregorian().strftime("%Y-%m-%d")
    time = dtstr[-8:]
    return f"{date} {time}"


def to_camel(string: str) -> str:
    return "".join(word.capitalize() for word in string.split("_"))


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

    @field_serializer(
        "audited",
        "not_audited",
        "mains",
        "childs",
        "consolidatable",
        "not_consolidatable",
        "publisher",
        "is_not_audited",
    )
    def serialize_bool(self, v: bool):
        return str(v).lower()


class Letter(BaseModel):
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

    @field_serializer("symbol", "company_name", "letter_code", "title")
    def serialize_norm_char(self, v: str):
        return norm_char(v)

    @field_serializer("sent_date_time", "publish_date_time")
    def serialize_datetime(self, v: str):
        return jalali_to_gregorian(norm_char(v))

    @field_serializer("url", "attachment_url", "pdf_url")
    def serialize_url(self, v: str):
        if v:
            if v[0] != "/":
                v = f"/{v}"
            return f"{self.base_url}{v}"


class ErrorLog(BaseModel):
    find_data: List[Tuple[str, str, str]] | List
    validate_json: List[Tuple[str, str, str]] | List


def to_camel_(string: str) -> str:
    l = []
    for i, word in enumerate(string.split("_")):
        if i == 0:
            l.append(word.lower())
        else:
            l.append(word.capitalize())
    return "".join(l)


class Cell(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel_, populate_by_name=True)

    address: str
    category: int
    cell_group_name: str
    col_span: int
    column_code: int
    column_sequence: int
    decimal_place: int
    period_end_to_date: str
    row_code: int
    row_sequence: int
    row_span: int
    row_type_name: str
    value: str
    value_type_name: str
    year_end_to_date: str


class Table(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel_, populate_by_name=True)

    sequence: int
    sheet_code: int
    version_no: str
    alias_name: str | None
    cells: List[Cell]


class Sheet(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel_, populate_by_name=True)

    version_no: int
    alias_name: str
    code: int
    sequence: int
    tables: List[Table]


class IncumeStatements(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel_, populate_by_name=True)

    is_audited: bool
    period: int
    period_end_to_date: str
    period_extra_day: int
    register_date_time: str
    sent_date_time: str | None
    sheets: List[Sheet]
    type: int
    year_end_to_date: str


is_items = {
    "درآمدهاي عملياتي": "sales",
    "بهاى تمام شده درآمدهاي عملياتي": "cost_of_goods_sold",
    "سود(زيان) ناخالص": "gross_profit",
    "هزينه‏ هاى فروش، ادارى و عمومى": "marketing_general_and_administrative_expenses",
    "هزينه کاهش ارزش دريافتني‏ ها (هزينه استثنايي)": "special_items",
    "ساير درآمدها": "other_operating_income",
    "سایر درآمدهای عملیاتی": "other_operating_income",
    "سایر هزینه ها": "other_operating_expense",
    "سایر هزینه‌های عملیاتی": "other_operating_expense",
    "سود(زيان) عملياتى": "operating_income",
    "هزينه‏ هاى مالى": "interest_expense",
    "ساير درآمدها و هزينه ‏هاى غيرعملياتى": "other_income",
    "سایر درآمدها و هزینه‌های غیرعملیاتی- درآمد سرمایه‌گذاری‌ها": "other_income",
    "سایر درآمدها و هزینه‌های غیرعملیاتی- اقلام متفرقه": "other_income",
    "سود(زيان) عمليات در حال تداوم قبل از ماليات": "income_from_continuing_operations_before_taxes",
    "مالیات بر درآمد": "income_tax",
    "سال جاري": "income_tax",
    "سال‌هاي قبل": "income_tax",
    "سود(زيان) خالص عمليات در حال تداوم": "net_income_from_continuing_operations",
    "سود (زيان) خالص عمليات متوقف شده": "income_from_discontinued_operations_net_of_tax",
    "سود (زیان) عملیات متوقف ‌شده پس از اثر مالیاتی": "income_from_discontinued_operations_net_of_tax",
    "سود(زيان) خالص": "net_income",
    "سود (زيان) خالص هر سهم – ريال": "eps",
    "سرمایه": "listed_capital",
}


def normalize_fs_item(w: str):
    dict_ = {
        " ": "",
        "–": "",
        "(": "",
        ")": "",
        "،": "",
        "ي": "ی",
        "ى": "ی",
        "آ": "ا",
        "\u200f": "",
        "\u200c": "",
    }
    return w.translate(str.maketrans(dict_))


def translate(item: str, dict_: dict):
    for k, v in dict_.items():
        if item and normalize_fs_item(k) == normalize_fs_item(item):
            return v
    return item


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

        validate_json_log = []
        data = []
        for i in json_list:
            try:
                data.append(IncumeStatements.model_validate_json(norm_char(i)))
            except ValidationError as e:
                validate_json_log.append(
                    ("نتونستم این جیسون رو اعتبار سنجی کنم.", i, e)
                )
        select = [
            "sales",
            "cost_of_goods_sold",
            "gross_profit",
            "marketing_general_and_administrative_expenses",
            "special_items",
            "other_operating_income",
            "other_operating_expense",
            "operating_income",
            "interest_expense",
            "other_income",
            "income_from_continuing_operations_before_taxes",
            "income_tax",
            "net_income_from_continuing_operations",
            "income_from_discontinued_operations_net_of_tax",
            "net_income",
            "eps",
            "listed_capital",
        ]
        if not isinstance(data, list):
            data = [data]
        df = pl.DataFrame()

        for i in data:
            if i.sheets[0].tables[0].alias_name == "IncomeStatement":
                cells = i.sheets[0].tables[0].cells
            elif i.sheets[0].tables[1].alias_name == "IncomeStatement":
                cells = i.sheets[0].tables[1].cells
            cells = [(i.column_sequence, i.row_sequence, i.value) for i in cells]
            df_ = pl.from_records(cells, schema=["col", "row", "value"])
            df_ = (
                df_.pivot(values="value", columns="col", index="row")
                .rename({"1": "item", "2": "value"})
                .select(["item", "value"])
            )
            df_ = df_.with_columns(
                pl.struct(["item"]).map_elements(
                    lambda x: translate(x["item"], is_items)
                )
            )
            df_ = df_.filter(pl.col("item").is_in(select))
            df_ = df_.with_columns(
                [
                    pl.col("value").cast(pl.Int64, strict=False).fill_null(0),
                    pl.lit(1).alias("row"),
                ]
            )

            net_income = df_.filter(pl.col("item") == "net_income")["value"]

            df_ = df_.pivot(
                values="value", columns="item", index="row", aggregate_function="sum"
            )
            df_ = df_.with_columns(pl.lit(net_income.max()).alias("net_income"))
            if "special_items" not in df_.columns:
                df_ = df_.with_columns(pl.lit(0).cast(pl.Int64).alias("special_items"))
            df_ = df_.select(select)
            df_ = df_.with_columns(
                [
                    pl.lit(i.is_audited).alias("is_audited"),
                    pl.lit(i.period_end_to_date if i.period_end_to_date else "").alias(
                        "period_end_to_date"
                    ),
                    pl.lit(i.year_end_to_date if i.year_end_to_date else "").alias(
                        "year_end_to_date"
                    ),
                    pl.lit(i.register_date_time if i.register_date_time else "").alias(
                        "register_date_time"
                    ),
                    pl.lit(i.sent_date_time if i.sent_date_time else "").alias(
                        "sent_date_time"
                    ),
                ]
            )
            df = pl.concat([df, df_])
        error_log = ErrorLog(find_data=find_data_log, validate_json=validate_json_log)
        return df, error_log
