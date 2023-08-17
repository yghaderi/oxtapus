import jdatetime
from collections import namedtuple
import re
import json
import pandas as pd
from .columns import cols

Ced = namedtuple(
    "RahavardCed", ["parser", "balance_sheet", "income_statements", "cash_flow"]
)


# ------------ Rahavard 356 -------------
def rahavard_parser(t, split0="var layoutModel =", split1=";"):
    t = t.split(split0)[1].split(split1)[0].strip()
    return json.loads(t)


def balance_sheet(bs: json):
    bs = rahavard_parser(bs)
    meta = pd.json_normalize(
        bs.get("balance_sheets") * len(bs.get("balance_sheet_field_items"))
    )
    data = pd.json_normalize(bs.get("balance_sheet_field_items"), record_path="items")
    df = meta.join(data)
    df = df.pivot_table(
        index=["date_time", "jalali_date_time", "fiscal_year", "jalali_fiscal_year"],
        columns="field.english_title",
        values=["value"],
    )
    df.columns = df.columns.get_level_values(1)
    df.reset_index(inplace=True)
    return df.rename(columns=cols.balance_sheet.rename)


def income_statements(is_: json):
    is_ = rahavard_parser(is_, split0="var viewModel =")
    meta = pd.json_normalize(
        is_.get("profit_losses") * len(is_.get("profit_loss_field_items"))
    )
    data = pd.json_normalize(is_.get("profit_loss_field_items"), record_path="items")
    df = meta.join(data)
    df = df.pivot_table(
        index=["date_time", "jalali_date_time", "fiscal_year", "jalali_fiscal_year"],
        columns="field.english_title",
        values=["value"],
    )
    df.columns = df.columns.get_level_values(1)
    df.reset_index(inplace=True)
    return df.rename(columns=cols.income_statements.rename)


def cash_flow(cf: json):
    cf = rahavard_parser(cf)
    meta = pd.json_normalize(
        cf.get("cash_flows") * len(cf.get("cash_flow_field_items"))
    )
    data = pd.json_normalize(cf.get("cash_flow_field_items"), record_path="items")
    print(data["fild"])
    df = meta.join(data)
    print(df.columns)
    df = df.pivot_table(
        index=["date_time", "jalali_date_time", "fiscal_year", "jalali_fiscal_year"],
        columns="field.english_title",
        values=["value"],
    )
    df.columns = df.columns.get_level_values(1)
    df.reset_index(inplace=True)
    return df.rename(columns=cols.cash_flow.rename)


ced = Ced(
    parser=rahavard_parser,
    balance_sheet=balance_sheet,
    income_statements=income_statements,
    cash_flow=cash_flow,
)
