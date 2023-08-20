from collections import namedtuple
from hazm import Normalizer
import re
import json
import pandas as pd
from .columns import cols
from ...utils import get
from .fs_items import fs_items

normalizer = Normalizer()
Ced = namedtuple("Ced", ["letters", "balance_sheet", "income_statements", "cash_flows"])


# ------------- ****** -------------
def codal_parser(text):
    t = text.split("var datasource =")[1].split("};")[0].strip() + "}"
    return json.loads(t)


def arabic_char(s: str):
    return s.translate(str.maketrans({"ي": "ی", "ك": "ک"}))


def match_date(t):
    t = t.replace("/", "-")
    try:
        return re.findall("\d{1,4}-\d{1,2}-\d{2,4}", t)[0]
    except:
        print(("enter valid text to match date"))


# ------------- letters -------------
def letters(url):
    pass


# ------------- balance_sheet -------------
def balance_sheet():
    pass


# ------------- income_statements -------------


def clean_income_statements(df):
    df = df[[1, 2]]
    df.columns = ["item", match_date(df[df[1] == "شرح"][2].values[0])]
    df.item = (
        df.item.fillna("").map(normalizer.normalize).map(fs_items.income_statements)
    )
    df.dropna(inplace=True)
    df.iloc[:, 1] = pd.to_numeric(df.iloc[:, 1], errors="raise")
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    df = df.groupby("item").sum().reset_index()
    df = (
        df.pivot_table(columns=["item"], aggfunc=sum)
        .reset_index()
        .rename(columns={"index": "period_end_to_date"})
    )
    df.columns.set_names(None, inplace=True)
    return df


def income_statements(url):
    r = get(url, verify=True, timeout=(2, 10))
    dict_ = codal_parser(r.text)
    records = dict_["sheets"][0]["tables"][0]["cells"]
    if dict_["sheets"][0]["tables"][1]["aliasName"] == "IncomeStatement":
        records = dict_["sheets"][0]["tables"][1]["cells"]
    df = pd.DataFrame()
    for i in records:
        df.loc[i.get("rowCode"), i.get("columnCode")] = i.get("value")
    return clean_income_statements(df.sort_index())


# ------------- cash_flows -------------
def cash_flows():
    pass


ced = Ced(
    letters=letters,
    balance_sheet=balance_sheet,
    income_statements=income_statements,
    cash_flows=cash_flows,
)
