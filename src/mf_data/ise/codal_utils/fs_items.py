from collections import namedtuple
from hazm import Normalizer

normalizer = Normalizer()

FSItems = namedtuple("FSItems", ["income_statements"])

income_statements = {
    "درآمدهای عملیاتی": "revenue",
    "بهاى تمام شده درآمدهای عملیاتی": "cost_of_goods_sold",
    "سود (زيان) ناخالص": "gross_profit",
    "هزينه‏‌هاى فروش، ادارى و عمومى": "sales_general_and_administrative_expense",
    "هزينه‏ هاى فروش، ادارى و عمومى": "sales_general_and_administrative_expense",
    "هزینه کاهش ارزش دریافتنی‌‏ها (هزینه استثنایی)": "cost_of_decrease_in_receivables_value(exceptional_cost)",
    "هزينه کاهش ارزش دريافتني‏ ها (هزينه استثنايي)": "cost_of_decrease_in_receivables_value(exceptional_cost)",
    "ساير درآمدها": "other_operating_revenue",
    "سایر هزینه‌ها": "other_operating_expenses",
    "سود (زيان) عملياتي": "operating_income",
    "هزينه‏‌هاى مالى": "finance_expense",
    "هزينه‏ هاى مالى": "finance_expense",
    "ساير درآمدها و هزينه ‏هاى غيرعملياتى": "net_miscellaneous_revenue",
    "سایر درآمدها و هزینه‌های غیرعملیاتی- درآمد سرمایه‌گذاری‌ها": "net_miscellaneous_revenue",
    "سایر درآمدها و هزینه‌های غیرعملیاتی- اقلام متفرقه": "net_miscellaneous_revenue",
    "سود (زيان) عمليات در حال تداوم قبل از ماليات": "net_income_from_continuing_operations_before_tax",
    "سال جاری": "taxes",
    "سال‌های قبل": "taxes",
    "سود (زيان) خالص عمليات در حال تداوم": "net_income_from_continuing_operation",
    "سود (زیان) خالص عملیات متوقف شده": "discontinued_operations_profit",
    "سود (زيان) خالص عمليات متوقف شده": "discontinued_operations_profit",
    "سود (زيان) خالص": "net_income",
    "سود (زیان) خالص هر سهم– ریال": "earning_per_share",
    "سود (زيان) خالص هر سهم – ريال": "earning_per_share",
    "سرمایه": "listed_capital",
    # -------------------------------
    "بهای تمام \u200cشده درآمدهای عملیاتی": "cost_of_goods_sold",
    "سود (زیان) ناخالص": "gross_profit",
    "هزینه\u200cهای فروش، اداری و عمومی": "sales_general_and_administrative_expense",
    "سایر درآمدهای عملیاتی": "other_operating_revenue",
    "سایر هزینه\u200cهای عملیاتی": "other_operating_expenses",
    "سود (زیان) عملیاتی": "operating_income",
    "هزینه\u200cهای مالی": "finance_expense",
    "هزینه‏‌های مالی": "finance_expense",
    "سایر درآمدها و هزینه\u200cهای غیرعملیاتی- درآمد سرمایه\u200cگذاری\u200cها": "net_miscellaneous_revenue",
    "سود (زیان) عملیات در حال تداوم قبل از مالیات": "net_income_from_continuing_operations_before_tax",
    "مالیات بر درآمد": "taxes",
    "سود (زیان) خالص عملیات در حال تداوم": "net_income_from_continuing_operation",
    "سود (زیان) عملیات متوقف \u200cشده پس از اثر مالیاتی": "discontinued_operations_profit",
    "سود (زیان) خالص": "net_income",
    "سود (زیان) خالص هر سهم– ریال": "earning_per_share",
}


def normalize_key(dict_: dict):
    return {normalizer.normalize(key): val for key, val in dict_.items()}


fs_items = FSItems(income_statements=normalize_key(income_statements))
