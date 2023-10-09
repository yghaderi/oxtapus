import jdatetime
from collections import namedtuple
import re
import pandas as pd
from .columns import cols

Ced = namedtuple(
    "Ced",
    [
        "mw",
        "omw",
        "arabic_char",
        "ins_info",
        "date",
        "adj_price",
        "index_traker_symbols",
        "last_ins_info",
    ],
)


def mw(df):
    """
    :param df:
    :return:
    """
    return df.rename(columns=cols.mw.rename).rename(columns=cols.mw_ob.rename)[
        cols.mw.rep + cols.mw_ob.rep
    ]


def date(df: pd.DataFrame, jdate: bool = True):
    df["date"] = pd.to_datetime(df.date.astype(str)).dt.date
    if jdate:
        df["jdate"] = df.date.map(
            lambda x: jdatetime.datetime.fromgregorian(datetime=x).date()
        )
    return df.set_index("date").sort_index()


def adj_price(df):
    """
    adjust price after capital increase, dividend, ... base on yesterday-close
    :param df: pandas.DataFrame, contain (y_final, final, open, high, low, close) columns
    :return: pandas.DataFrame
    """
    df["coef"] = (df["y_final"].shift(-1) / df["final"]).fillna(1.0)
    df["adj_coe"] = df.iloc[::-1]["coef"].cumprod().iloc[::-1]
    df[["adj_open", "adj_high", "adj_low", "adj_close", "adj_final"]] = (
        (df[["open", "high", "low", "close", "final"]].T * df["adj_coe"]).T
    ).applymap(int)
    df.drop(columns=["coef", "adj_coe", "y_final"], inplace=True)
    return df


def arabic_char(s: str):
    return s.translate(str.maketrans({"ي": "ی", "ك": "ک"}))


def option_type(s: str):
    return "call" if s.startswith("ض") else "put"


def expiration_date(s: str):
    ex_date = re.findall("[0-9]+", s)
    ex_date = "".join(ex_date)
    match len(ex_date):
        case 8:
            return f"{ex_date[:4]}-{ex_date[4:6]}-{ex_date[6:8]}"
        case 6:
            return f"14{ex_date[:2]}-{ex_date[2:4]}-{ex_date[4:6]}"


def days_to_ex_date(ex_date):
    y, m, d = map(int, (tuple(ex_date.split("-"))))
    return (jdatetime.date(y, m, d) - jdatetime.date.today()).days


def underlying_asset(s: str):
    return s[4:8]


def omw(option: pd.DataFrame, ua: pd.DataFrame):
    option[["ua", "strike_price", "ex_date"]] = option.name_far.str.split(
        "-", expand=True
    )
    option.loc[:, "ua"] = option["ins_id"].map(underlying_asset)
    ua.loc[:, "ua"] = ua["ua_ins_id"].map(underlying_asset)
    df = option.merge(ua, on="ua", how="inner")
    df = df[~df.ex_date.isnull()].copy()
    df = df.assign(ex_date=df.ex_date.map(expiration_date))
    df = df.apply(pd.to_numeric, errors="ignore")
    df = df.assign(
        t=df.ex_date.map(days_to_ex_date), type=df.symbol_far.map(option_type)
    )
    return df


def ins_info(instrument_info: str):
    return {
        "ins_code": instrument_info["insCode"],
        "ins_id": instrument_info["instrumentID"],
        "symbol": instrument_info["cIsin"][4:8],
        "name": instrument_info["lVal18"],
        "symbol_far": instrument_info["lVal18AFC"],
        "name_far": instrument_info["lVal30"],
        "capital": instrument_info["zTitad"],
        "sector_name": instrument_info["sector"]["lSecVal"],
        "sector_code": instrument_info["sector"]["cSecVal"].replace(" ", ""),
        "group_type": instrument_info["cgrValCot"],
        "market_name": instrument_info["flowTitle"],
        "market_code": instrument_info["flow"],
        "market_type": instrument_info["cgrValCotTitle"],
        "base_vol": instrument_info["baseVol"],
        "eps": instrument_info["eps"]["estimatedEPS"],
        "float_shares_pct": instrument_info["kAjCapValCpsIdx"],
        "contract_size": instrument_info["contractSize"],
    }


def index_traker_symbols(index_code: int, data: dict):
    """Parse index traker symbols data
    :param index_code: int
    :param data: dict
    :return list of dict
    """
    return [
        {
            "industry_code": index_code,
            "instrument_code": ins["instrument"]["insCode"],
            "symbol_far": ins["instrument"]["lVal18AFC"],
        }
        for ins in data
    ]


def last_ins_info(last_info: dict) -> dict:
    return {**last_info.pop("instrumentState"), **last_info}


ced = Ced(
    mw=mw,
    omw=omw,
    arabic_char=arabic_char,
    ins_info=ins_info,
    date=date,
    adj_price=adj_price,
    index_traker_symbols=index_traker_symbols,
    last_ins_info=last_ins_info,
)
