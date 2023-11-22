from dataclasses import dataclass
import polars as pl

__all__ = ["manipulation_cols", "cols"]


@dataclass
class ManipulationCols:
    rename: dict | None
    prefix: str | None
    suffix: str | None
    select: list[str] | None
    drop: list[str] | None


@dataclass
class TSETMC:
    mw: ManipulationCols
    mw_orderbook: ManipulationCols
    options_mw: ManipulationCols
    options_ua_mw: ManipulationCols
    specific_option_data: ManipulationCols
    hist_price: ManipulationCols
    intraday_trades: ManipulationCols
    last_ins_data: ManipulationCols
    client_type: ManipulationCols
    share_change: ManipulationCols
    indexes: ManipulationCols
    index_hist: ManipulationCols


@dataclass
class Cols:
    tsetmc: TSETMC


def manipulation_cols(df: pl.DataFrame, columns: ManipulationCols):
    if columns.rename:
        df = df.rename(columns.rename)
    if columns.prefix:
        df = df.rename({i: f"{columns.prefix}{i}" for i in df.columns})
    if columns.suffix:
        df = df.rename({i: f"{i}{columns.suffix}" for i in df.columns})
    if columns.select:
        df = df.select(columns.select)
    if columns.drop:
        df = df.drop(columns.drop)
    return df


########################################################################################################
#   ######## TSETMC
########################################################################################################

mw = ManipulationCols(
    rename={
        "insCode": "ins_code",
        "insID": "ins_id",
        "lva": "symbol",
        "lvc": "name",
        "eps": "eps",
        "pe": "pe",
        "pmd": "bid",
        "pmo": "ask",
        "pf": "open",
        "pmx": "high",
        "pmn": "low",
        "pdv": "close",
        "pcl": "final",
        "py": "y_final",
        "qtc": "value",
        "qtj": "volume",
        "ztt": "trade_count",
        "pMax": "max_lim",
        "pMin": "min_lim",
        "ztd": "capital",
        "bv": "base_volume",
        "hEven": "event_time",
    },
    suffix=None,
    prefix=None,
    select=[
        "ins_code",
        "ins_id",
        "symbol",
        "name",
        "eps",
        "pe",
        "open",
        "high",
        "low",
        "close",
        "final",
        "y_final",
        "value",
        "volume",
        "trade_count",
        "max_lim",
        "min_lim",
        "capital",
        "base_volume",
        "event_time",
        "ob_level",
        "bid_count",
        "bid_size",
        "bid_price",
        "ask_price",
        "ask_size",
        "ask_count",
    ],
    drop=None,
)

mw_orderbook = ManipulationCols(
    rename={
        "ob_n": "ob_level",
        "ob_zmd": "bid_count",
        "ob_qmd": "bid_size",
        "ob_pmd": "bid_price",
        "ob_pmo": "ask_price",
        "ob_qmo": "ask_size",
        "ob_zmo": "ask_count",
    },
    suffix=None,
    prefix=None,
    select=None,
    drop=None,
)

options_mw = ManipulationCols(
    rename={"capital": "lot_size"},
    suffix=None,
    prefix=None,
    select=None,
    drop=["eps", "pe", "bid", "ask", "base_volume"],
)

options_ua_mw = ManipulationCols(
    rename=None,
    suffix=None,
    prefix="ua_",
    select=None,
    drop=None,
)

specific_option_data = ManipulationCols(
    rename={
        "insCode": "ins_code",
        "instrumentID": "ins_id",
        "buyOP": "open_interest",
        "contractSize": "lot_size",
        "strikePrice": "k",
        "uaInsCode": "ua_ins_code",
        "beginDate": "listed_date",
        "endDate": "ex_date",
    },
    suffix=None,
    prefix=None,
    select=[
        "ins_code",
        "ins_id",
        "ua_ins_code",
        "listed_date",
        "ex_date",
        "lot_size",
        "k",
        "open_interest",
    ],
    drop=None,
)

hist_price = ManipulationCols(
    rename={
        "insCode": "ins_code",
        "dEven": "date",
        "priceFirst": "open",
        "priceMax": "high",
        "priceMin": "low",
        "pDrCotVal": "close",
        "pClosing": "final",
        "priceYesterday": "y_final",
        "qTotTran5J": "volume",
        "qTotCap": "value",
        "zTotTran": "trade_count",
    },
    suffix=None,
    prefix=None,
    select=[
        "date",
        "ins_code",
        "open",
        "high",
        "low",
        "close",
        "final",
        "y_final",
        "volume",
        "value",
        "trade_count",
    ],
    drop=None,
)
intraday_trades = ManipulationCols(
    rename={
        "nTran": "trade_nbr",
        "hEven": "time",
        "qTitTran": "volume",
        "pTran": "price",
    },
    suffix=None,
    prefix=None,
    select=["datetime", "trade_nbr", "price", "volume"],
    drop=None,
)

last_ins_data = ManipulationCols(
    rename={
        "cEtaval": "status",
        "cEtavalTitle": "status_far",
        "lastHEven": "time",
        "finalLastDate": "date",
        "priceMin": "low",
        "priceMax": "high",
        "priceYesterday": "y_final",
        "priceFirst": "open",
        "dEven": "event_date",
        "hEven": "event_time",
        "pClosing": "final",
        "iClose": "i_close",
        "yClose": "y_close",
        "pDrCotVal": "close",
        "zTotTran": "trade_count",
        "qTotTran5J": "volume",
        "qTotCap": "value",
    },
    suffix=None,
    prefix=None,
    select=[
        "date",
        "time",
        "status",
        "status_far",
        "open",
        "low",
        "high",
        "close",
        "final",
        "y_final",
        "trade_count",
        "volume",
        "value",
        "event_date",
        "event_time",
        "i_close",
        "y_close",
    ],
    drop=None,
)
client_type = ManipulationCols(
    rename={
        "recDate": "date",
        "insCode": "ins_code",
        "buy_I_Count": "buyers_count_ind",
        "buy_N_Count": "buyers_count_ins",
        "sell_I_Count": "sellers_count_ind",
        "sell_N_Count": "sellers_count_ins",
        "buy_I_Volume": "vol_purchase_ind",
        "buy_N_Volume": "vol_purchase_ins",
        "sell_I_Volume": "vol_sales_ind",
        "sell_N_Volume": "vol_sales_ins",
        "buy_I_Value": "val_purchase_ind",
        "buy_N_Value": "val_purchase_ins",
        "sell_I_Value": "val_sales_ind",
        "sell_N_Value": "val_sales_ins",
    },
    suffix=None,
    prefix=None,
    select=None,
    drop=None,
)

share_change = ManipulationCols(
    rename={
        "insCode": "ins_code",
        "dEven": "date",
        "numberOfShareNew": "current",
        "numberOfShareOld": "previous",
    },
    suffix=None,
    prefix=None,
    select=["date", "ins_code", "previous", "current"],
    drop=None,
)
indexes = ManipulationCols(
    rename={
        "insCode": "ind_code",
        "lVal30": "name",
        "hEven": "time",
        "xDrNivJIdx004": "close",
        "xPbNivJIdx004": "low",
        "xPhNivJIdx004": "high",
        "indexChange": "change",
        "xVarIdxJRfV": "pct_change",
    },
    suffix=None,
    prefix=None,
    select=["ind_code", "name", "time", "close", "low", "high", "change", "pct_change"],
    drop=None,
)

index_hist = ManipulationCols(
    rename={
        "insCode": "ind_code",
        "dEven": "date",
        "xNivInuClMresIbs": "close",
        "xNivInuPbMresIbs": "low",
        "xNivInuPhMresIbs": "high",
    },
    suffix=None,
    prefix=None,
    select=["date", "ind_code", "close", "low", "high"],
    drop=None,
)

tsetmc = TSETMC(
    mw=mw,
    mw_orderbook=mw_orderbook,
    options_mw=options_mw,
    options_ua_mw=options_ua_mw,
    specific_option_data=specific_option_data,
    hist_price=hist_price,
    intraday_trades=intraday_trades,
    last_ins_data=last_ins_data,
    client_type=client_type,
    share_change=share_change,
    indexes=indexes,
    index_hist=index_hist,
)

########################################################################################################
#   ######## cols
########################################################################################################
cols = Cols(tsetmc=tsetmc)
