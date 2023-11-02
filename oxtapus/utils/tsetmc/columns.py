from dataclasses import dataclass
from oxtapus.utils import ManipulationCols

__all__ = ["cols"]


@dataclass
class Cols:
    mw: ManipulationCols
    mw_orderbook: ManipulationCols
    options_mw: ManipulationCols
    options_ua_mw: ManipulationCols


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
cols = Cols(
    mw=mw, mw_orderbook=mw_orderbook, options_mw=options_mw, options_ua_mw=options_ua_mw
)
