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
        "buyOP": "open_interest",
        "contractSize": "lot_size",
        "strikePrice": "k",
        "uaInsCode": "ua_ins_code",
        "beginDate": "begin_date",
        "endDate": "ex_date",
    },
    suffix=None,
    prefix=None,
    select=["ins_code",
            "ua_ins_code",
            "begin_date",
            "ex_date",
            "lot_size",
            "k",
            "open_interest"],
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
        "zTotTran": "trade_count"
    },
    suffix=None,
    prefix=None,
    select=[
        "ins_code",
        "date",
        "open",
        "high",
        "low",
        "close",
        "final",
        "y_final",
        "volume",
        "value",
        "trade_count"
    ],
    drop=None,

)

tsetmc = TSETMC(
    mw=mw, mw_orderbook=mw_orderbook, options_mw=options_mw, options_ua_mw=options_ua_mw,
    specific_option_data=specific_option_data, hist_price=hist_price
)

########################################################################################################
#   ######## cols
########################################################################################################
cols = Cols(
    tsetmc=tsetmc
)
