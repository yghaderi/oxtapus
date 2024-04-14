import datetime as dt
from pydantic import BaseModel, Field, field_validator


class MarketWatchOrderBook(BaseModel):
    ob_level: int = Field(alias="n")
    bid_count: int = Field(alias="zmd")
    bid_size: float = Field(alias="qmd")
    bid_price: float = Field(alias="pmd")
    ask_price: float = Field(alias="pmo")
    ask_size: float = Field(alias="qmo")
    ask_count: int = Field(alias="zmo")


class ClientTypeAll(BaseModel):
    ins_code: str = Field(alias="insCode")
    buy_vol_ind: float = Field(alias="buy_I_Volume")
    buy_vol_ins: float = Field(alias="buy_N_Volume")
    buy_count_ind: int = Field(alias="buy_CountI")
    buy_count_ins: int = Field(alias="buy_CountN")
    sell_vol_ind: float = Field(alias="sell_I_Volume")
    sell_vol_ins: float = Field(alias="sell_N_Volume")
    sell_count_ind: int = Field(alias="sell_CountI")
    sell_count_ins: int = Field(alias="sell_CountN")


class MarketWatch(BaseModel):
    ins_code: str = Field(alias="insCode")
    ins_id: str = Field(alias="insID")
    symbol: str = Field(alias="lva")
    name: str = Field(alias="lvc")
    eps: float = Field(alias="eps")
    pe: float = Field(alias="pe")
    bid: float = Field(alias="pmd")  #
    ask: float = Field(alias="pmo")  #
    open: float = Field(alias="pf")
    high: float = Field(alias="pmx")
    low: float = Field(alias="pmn")
    close: float = Field(alias="pdv")
    final: float = Field(alias="pcl")
    y_final: float = Field(alias="py")
    value: float = Field(alias="qtc")
    volume: float = Field(alias="qtj")
    trade_count: float = Field(alias="ztt")
    max_lim: float = Field(alias="pMax")
    min_lim: float = Field(alias="pMin")
    capital: float = Field(alias="ztd")
    base_volume: float = Field(alias="bv")
    event_time: float = Field(alias="hEven")
    order_book: list[MarketWatchOrderBook] = Field(alias="blDs")

    @field_validator("pe", mode="before")
    def parce_pe(cls, value):
        try:
            return float(value)
        except ValueError:
            return 0.0
        except TypeError:
            return 0.0


class HistPrice(BaseModel):
    date: dt.date = Field(alias="dEven")
    ins_code: str = Field(alias="insCode")
    open: float = Field(alias="priceFirst")
    high: float = Field(alias="priceMax")
    low: float = Field(alias="priceMin")
    close: float = Field(alias="pDrCotVal")
    final: float = Field(alias="pClosing")
    y_final: float = Field(alias="priceYesterday")
    volume: float = Field(alias="qTotTran5J")
    value: float = Field(alias="qTotCap")
    trade_count: float = Field(alias="zTotTran")

    @field_validator("date", mode="before")
    def parse_date(cls, value):
        return dt.datetime.strptime(str(value), "%Y%m%d").date()
