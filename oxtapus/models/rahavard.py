from pydantic import BaseModel


class BalanceSheetItemsField(BaseModel):
    title: str
    english_title: str
    account: str
    is_parent: bool
    parent: str
    index_view: int
    id: str
    sign_neg: bool
    sign_pos: bool
    neg_nature: bool


class BalanceSheetItems(BaseModel):
    field: BalanceSheetItemsField
    value: int


class FinancialViewType(BaseModel):
    id: str


class BalanceSheetData(BaseModel):
    date: str
    fiscal_year: str
    announcement_type: str
    financial_view_type: FinancialViewType
    report_id: str
    id: str
    items: list[BalanceSheetItems]


class BalanceSheet(BaseModel):
    data: list[BalanceSheetData]
