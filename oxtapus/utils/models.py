import datetime as dt
from pydantic import BaseModel, Field, field_validator


class AdjustPriceFlow(BaseModel):
    ins_code: str = Field(alias="insCode")
    symbol: str = Field(alias="lVal18AFC")
    date: dt.date = Field(alias="dEven")
    adj_final: float = Field(alias="pClosing")
    final: float = Field(alias="pClosingNotAdjusted")

    @field_validator("date", mode="before")
    def parse_birthdate(cls, value):
        return dt.datetime.strptime(str(value), "%Y%m%d").date()


class InsShareChangeFlow(BaseModel):
    ins_code: str = Field(alias="insCode")
    symbol: str = Field(alias="lVal18AFC")
    date: dt.date = Field(alias="dEven")
    current_shares: int = Field(alias="numberOfShareNew")
    previous_shares: int = Field(alias="numberOfShareOld")

    @field_validator("date", mode="before")
    def parse_date(cls, value):
        return dt.datetime.strptime(str(value), "%Y%m%d").date()


class OptionsMW(BaseModel):
    ins_code_ua: str = Field(alias="uaInsCode")
    symbol_ua: str = Field(alias="lval30_UA")
    close_ua: int = Field(alias="pDrCotVal_UA")
    final_ua: int = Field(alias="pClosing_UA")
    y_final_ua: int = Field(alias="priceYesterday_UA")
    contract_size: int = Field(alias="contractSize")
    begin_date: str = Field(alias="beginDate")
    end_date: str = Field(alias="endDate")
    k: int = Field(alias="strikePrice")
    t: int = Field(alias="remainedDay")
    ins_code_c: str = Field(alias="insCode_C")
    symbol_c: str = Field(alias="lVal18AFC_C")
    name_c: str = Field(alias="lVal30_C")
    notional_val_c: int = Field(alias="notionalValue_C")
    y_open_interest_c: int = Field(alias="yesterdayOP_C")
    open_interest_c: int = Field(alias="oP_C")
    trade_count_c: int = Field(alias="zTotTran_C")
    trade_vol_c: int = Field(alias="qTotTran5J_C")
    trade_val_c: int = Field(alias="qTotCap_C")
    y_final_c: int = Field(alias="priceYesterday_C")
    final_c: int = Field(alias="pClosing_C")
    close_c: int = Field(alias="pDrCotVal_C")
    bid_price_c: int = Field(alias="pMeDem_C")
    bid_size_c: int = Field(alias="qTitMeDem_C")
    ask_price_c: int = Field(alias="pMeOf_C")
    ask_size_c: int = Field(alias="qTitMeOf_C")
    ask_size_p: int = Field(alias="qTitMeOf_P")
    ask_price_p: int = Field(alias="pMeOf_P")
    bid_price_p: int = Field(alias="pMeDem_P")
    bid_size_p: int = Field(alias="qTitMeDem_P")
    close_p: int = Field(alias="pDrCotVal_P")
    final_p: int = Field(alias="pClosing_P")
    y_final_p: int = Field(alias="priceYesterday_P")
    trade_val_p: int = Field(alias="qTotCap_P")
    trade_vol_p: int = Field(alias="qTotTran5J_P")
    trade_count_p: int = Field(alias="zTotTran_P")
    open_interest_p: int = Field(alias="oP_P")
    y_open_interest_p: int = Field(alias="yesterdayOP_P")
    notional_val_p: int = Field(alias="notionalValue_P")
    name_p: str = Field(alias="lVal30_P")
    symbol_p: str = Field(alias="lVal18AFC_P")
    ins_code_p: str = Field(alias="insCode_P")
