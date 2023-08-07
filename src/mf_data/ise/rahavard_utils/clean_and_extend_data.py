import jdatetime
from collections import namedtuple
import re
import json
import pandas as pd
from .columns import cols

Ced = namedtuple("RahavardCed", ["parser", "balance_sheet"])


# ------------ Rahavard 356 -------------
def rahavard_parser(t):
    t = t.split("var layoutModel =")[1].split(";")[0].strip()
    return json.loads(t)


def balance_sheet(bs: json):
    bs = rahavard_parser(bs)
    meta = pd.json_normalize(bs.get("balance_sheets") * len(bs.get("balance_sheet_field_items")))
    data = pd.json_normalize(bs.get("balance_sheet_field_items"), record_path="items")
    df = meta.join(data)
    df = df.pivot_table(index=["date_time", "jalali_date_time", "fiscal_year", "jalali_fiscal_year"],
                        columns='field.english_title', values=["value"])
    df.columns = df.columns.get_level_values(1)
    df.reset_index(inplace=True)
    return df.rename(columns=cols.bs.rename)


ced = Ced(parser=rahavard_parser, balance_sheet=balance_sheet)
