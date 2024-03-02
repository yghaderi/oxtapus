import datetime as dt
from pydantic import BaseModel, Field, field_validator


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

