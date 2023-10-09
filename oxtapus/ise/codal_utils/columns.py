from collections import namedtuple

Cols = namedtuple("Cols", ["letters", "income_statements", "balance_sheet"])
Property = namedtuple("Property", ["rename", "drop", "rep"])

_letters = {
    "rename": {
        "Symbol": "symbol",
        "CompanyName": "company_name",
        "Title": "title",
        "SentDateTime": "sent_datetime",
        "PublishDateTime": "issue_datetime",
        "HasAttachment": "has_attachment",
        "HasPdf": "has_pdf",
        "Url": "url",
        "AttachmentUrl": "attachment_url",
        "PdfUrl": "pdf_url",
        "ExcelUrl": "excel_url",
    },
    "rep": [
        "symbol",
        "company_name",
        "title",
        "sent_datetime",
        "issue_datetime",
        "has_attachment",
        "has_pdf",
        "url",
        "attachment_url",
        "pdf_url",
        "excel_url",
    ],
}

_income_statements = {
    "rep": [
        "symbol",
        "company_name",
        "title",
        "issue_datetime",
        "period_end_to_date",
        "revenue",
        "cost_of_goods_sold",
        "gross_profit",
        "sales_general_and_administrative_expense",
        "cost_of_decrease_in_receivables_value(exceptional_cost)",
        "other_operating_revenue",
        "other_operating_expenses",
        "operating_income",
        "finance_expense",
        "net_miscellaneous_revenue",
        "net_income_from_continuing_operations_before_tax",
        "taxes",
        "net_income_from_continuing_operation",
        "discontinued_operations_profit",
        "net_income",
        "earning_per_share",
        "listed_capital",
        "url",
    ]
}

_balance_sheet = {
    "rep": [
        "symbol",
        "company_name",
        "title",
        "issue_datetime",
        "period_end_to_date",
        "tangible_fixed_assets",
        "investment_property",
        "intangible_assets",
        "long_term_investments",
        "long_term_receivables",
        "other_assets",
        "total_non_current_assets",
        "prepayments",
        "inventories",
        "trade_and_other_receivables",
        "short_term_investments",
        "cash_and_equivalents",
        "asset_for_sale",
        "total_current_assets",
        "total_assets",
        "common_stock",
        "received_for_capital_advance",
        "capital_surplus",
        "treasury_stock_surplus",
        "legal_reserve",
        "expansion_reserve",
        "revaluation_surplus",
        "exchange_differences_on_translation",
        "retained_earnings",
        "treasury_stock",
        "total_shareholders_equity",
        "long_term_liabilities",
        "long_term_debt",
        "allowance_for_post_retirement",
        "total_non_current_liabilities",
        "trade_and_other_liabilities",
        "deferred_tax_liabilities",
        "dividends_payable",
        "loan_payable",
        "provisions",
        "deferred_revenue",
        "liabilities_related_to_assets_for_sale",
        "total_current_liabilities",
        "total_liabilities",
        "total_liabilities_and_shareholders_equities",
        "url",
    ]
}

letters = Property(
    rename=_letters.get("rename"), drop=_letters.get("drop"), rep=_letters.get("rep")
)
income_statements = Property(
    rename=_income_statements.get("rename"),
    drop=_income_statements.get("drop"),
    rep=_income_statements.get("rep"),
)
balance_sheet = Property(
    rename=_balance_sheet.get("rename"),
    drop=_balance_sheet.get("drop"),
    rep=_balance_sheet.get("rep"),
)

cols = Cols(
    letters=letters, income_statements=income_statements, balance_sheet=balance_sheet
)
