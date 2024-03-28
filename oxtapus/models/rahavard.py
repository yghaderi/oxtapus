from typing import Optional
from pydantic import BaseModel, field_validator
import datetime as dt

__all__ = ["Stocks", "BalanceSheet", "IncomeStatements", "CashFlow"]


class FSField(BaseModel):
    title: str
    english_title: str
    account: Optional[str] = "-"
    is_parent: bool
    parent: Optional[str]
    index_view: int
    id: str
    sign_neg: bool
    sign_pos: bool
    neg_nature: bool


class FSItems(BaseModel):
    field: FSField
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
    items: list[FSItems]

    @field_validator("date", "fiscal_year", mode="before")
    def parse_date(cls, value):
        return dt.datetime.strptime(
            str(value),
            "%Y-%m-%dT%H:%M:%S%z",
        ).date()


class BalanceSheet(BaseModel):
    data: list[BalanceSheetData]


class IncomeStatementsData(BaseModel):
    date: dt.date
    fiscal_year: dt.date
    announcement_type_id: str
    financial_view_type_id: str
    report_id: str
    capital: int
    id: str
    items: list[FSItems]

    @field_validator("date", "fiscal_year", mode="before")
    def parse_date(cls, value):
        return dt.datetime.strptime(
            str(value),
            "%Y-%m-%dT%H:%M:%S%z",
        ).date()


class IncomeStatements(BaseModel):
    data: list[IncomeStatementsData]


class CashFlowField(BaseModel):
    title: str
    english_title: str
    account: Optional[str] = "-"
    is_parent: bool
    index_view: int
    id: str


class CashFlowItems(BaseModel):
    field: CashFlowField
    value: float


class CashFlowData(BaseModel):
    date: dt.date
    fiscal_year: dt.date
    announcement_type_id: str
    financial_view_type_id: str
    report_id: str
    id: str
    items: list[CashFlowItems]


class CashFlow(BaseModel):
    data: list[CashFlowData]


class StocksData(BaseModel):
    name: str
    asset_id: str
    exchange_id: str


class Stocks(BaseModel):
    data: list[StocksData]
