from collections import namedtuple

Cols = namedtuple("Cols", ["letters", "income_statements"])
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
        "net_miscellaneous_revenue",
        "net_income_from_continuing_operations_before_tax",
        "taxes",
        "taxes",
        "net_income_from_continuing_operation",
        "discontinued_operations_profit",
        "net_income",
        "earning_per_share",
        "listed_capital",
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

cols = Cols(letters=letters, income_statements=income_statements)
