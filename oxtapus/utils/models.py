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
        return dt.datetime.strptime(
            str(value),
            "%Y%m%d"
        ).date()


class InsShareChangeFlow(BaseModel):
    ins_code: str = Field(alias="insCode")
    symbol: str = Field(alias="lVal18AFC")
    date: dt.date = Field(alias="dEven")
    current_shares: int = Field(alias="numberOfShareNew")
    previous_shares: int = Field(alias="numberOfShareOld")

    @field_validator("date", mode="before")
    def parse_birthdate(cls, value):
        return dt.datetime.strptime(
            str(value),
            "%Y%m%d"
        ).date()
