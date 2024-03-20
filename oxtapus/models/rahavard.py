from typing import Optional
from pydantic import BaseModel, field_validator
import datetime as dt

__all__ = ["BalanceSheet"]


class BalanceSheetItemsField(BaseModel):
    title: str
    english_title: str
    account: str
    is_parent: bool
    parent: Optional[str]
    index_view: int
    id: str
    sign_neg: bool
    sign_pos: bool
    neg_nature: bool


class BalanceSheetItems(BaseModel):
    field: BalanceSheetItemsField
    value: float


class FinancialViewType(BaseModel):
    id: str


class BalanceSheetData(BaseModel):
    date: dt.date
    fiscal_year: dt.date
    announcement_type: str
    financial_view_type: FinancialViewType
    report_id: str
    id: str
    items: list[BalanceSheetItems]

    @field_validator("date", "fiscal_year", mode="before")
    def parse_date(cls, value):
        return dt.datetime.strptime(str(value), "%Y-%m-%dT%H:%M:%S%z", ).date()


class BalanceSheet(BaseModel):
    data: list[BalanceSheetData]
