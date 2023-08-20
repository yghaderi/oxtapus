from collections import namedtuple

Cols = namedtuple(
    "Cols",
    [
        "mw",
        "mw_ob",
        "omw",
        "hist_price",
        "option_info",
        "client_type",
        "option_info_comp",
    ],
)
Property = namedtuple("Property", ["rename", "drop", "rep"])

_mw = {
    "rename": {
        "insCode": "ins_code",
        "insID": "ins_id",
        "lva": "symbol_far",
        "lvc": "name_far",
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
    "rep": [
        "ins_code",
        "ins_id",
        "symbol_far",
        "name_far",
        "eps",
        "pe",
        "bid",
        "ask",
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
    ],
}
_mw_ob = {
    "rename": {
        "ob_n": "quote",
        "ob_zmd": "buy_count",
        "ob_qmd": "buy_vol",
        "ob_pmd": "buy_price",
        "ob_pmo": "sell_price",
        "ob_qmo": "sell_vol",
        "ob_zmo": "sell_count",
    },
    "rep": [
        "quote",
        "buy_count",
        "buy_vol",
        "buy_price",
        "sell_price",
        "sell_vol",
        "sell_count",
    ],
}
_omw = {
    "rename": {"capital": "lot_size"},
    "drop": ["eps", "pe", "bid", "ask", "base_volume"],
}

_hist_price = {
    "rename": {
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
    }
}
_option_info = {
    "rep": [
        "ins_code",
        "ins_id",
        "symbol",
        "name",
        "symbol_far",
        "name_far",
        "market_name",
    ]
}
_client_type = {
    "rename": {
        "recDate": "date",
        "insCode": "ins_code",
        "buy_I_Count": "buyers_nbr_ind",
        "buy_N_Count": "buyers_nbr_ins",
        "sell_I_Count": "sellers_nbr_ind",
        "sell_N_Count": "sellers_nbr_ins",
        "buy_I_Volume": "vol_purchase_ind",
        "buy_N_Volume": "vol_purchase_ins",
        "sell_I_Volume": "vol_sales_ind",
        "sell_N_Volume": "vol_sales_ins",
        "buy_I_Value": "val_purchase_ind",
        "buy_N_Value": "val_purchase_ins",
        "sell_I_Value": "val_sales_ind",
        "sell_N_Value": "val_sales_ins",
    }
}
_option_info_comp = {
    "rename": {
        "insCode": "ins_code",
        "buyOP": "open_interest",
        "contractSize": "contract_size",
        "strikePrice": "strike_price",
        "uaInsCode": "ua_ins_code",
        "beginDate": "begin_date",
        "endDate": "ex_date",
    },
    "rep": [
        "ins_code",
        "ua_ins_code",
        "begin_date",
        "ex_date",
        "contract_size",
        "strike_price",
        "open_interest",
    ],
}
mw = Property(
    rename=_mw.get("rename"), drop=_mw.get("drop"), rep=_mw.get("rep")
)  # market-watch
mw_ob = Property(
    rename=_mw_ob.get("rename"), drop=_mw_ob.get("drop"), rep=_mw_ob.get("rep")
)  # market-watch order-book
omw = Property(
    rename=_omw.get("rename"), drop=_omw.get("drop"), rep=_omw.get("rep")
)  # market-watch
hist_price = Property(
    rename=_hist_price.get("rename"),
    drop=_hist_price.get("drop"),
    rep=_hist_price.get("rep"),
)  # history-price
option_info = Property(
    rename=_option_info.get("rename"),
    drop=_option_info.get("drop"),
    rep=_option_info.get("rep"),
)
client_type = Property(
    rename=_client_type.get("rename"),
    drop=_client_type.get("drop"),
    rep=_client_type.get("rep"),
)
option_info_comp = Property(
    rename=_option_info_comp.get("rename"),
    drop=_option_info_comp.get("drop"),
    rep=_option_info_comp.get("rep"),
)
cols = Cols(
    mw=mw,
    mw_ob=mw_ob,
    omw=omw,
    hist_price=hist_price,
    option_info=option_info,
    client_type=client_type,
    option_info_comp=option_info_comp,
)
