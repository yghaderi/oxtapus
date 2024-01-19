from typing import ClassVar
from typing import List, Literal, Tuple
from pydantic import BaseModel, ConfigDict, field_serializer, ValidationError
from utils import jalali_to_gregorian, norm_char


def to_camel(string: str) -> str:
    return "".join(word.capitalize() for word in string.split("_"))


#######################################################################################################################
# income statements ###################################################################################################
#######################################################################################################################
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
    from_date: str = "1396/01/01"

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


class IncomeStatements(BaseModel):
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


#######################################################################################################################
# ***** #########################################################################################################
#######################################################################################################################
