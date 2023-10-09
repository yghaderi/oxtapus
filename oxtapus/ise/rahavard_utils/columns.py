from collections import namedtuple

Cols = namedtuple("Cols", ["balance_sheet", "income_statements", "cash_flow"])
Property = namedtuple("Property", ["rename", "drop", "rep"])

_balance_sheet = {
    "rename": {"date_time": "issue_date", "jalali_date_time": "j_issue_date"}
}
_income_statements = {
    "rename": {"date_time": "issue_date", "jalali_date_time": "j_issue_date"}
}
_cash_flow = {"rename": {"date_time": "issue_date", "jalali_date_time": "j_issue_date"}}

balance_sheet = Property(
    rename=_balance_sheet.get("rename"),
    drop=_balance_sheet.get("drop"),
    rep=_balance_sheet.get("rep"),
)
income_statements = Property(
    rename=_income_statements.get("rename"),
    drop=_income_statements.get("drop"),
    rep=_income_statements.get("rep"),
)
cash_flow = Property(
    rename=_cash_flow.get("rename"),
    drop=_cash_flow.get("drop"),
    rep=_cash_flow.get("rep"),
)

cols = Cols(
    balance_sheet=balance_sheet,
    income_statements=income_statements,
    cash_flow=cash_flow,
)
