import datetime as dt
from pydantic import BaseModel, Field, field_validator


class AdjustPrice(BaseModel):
    ins_code:str = Field(alias="insCode")
    symbol:str = Field(alias="lVal18AFC")
    date:dt.date = Field(alias="dEven")
    adj_final: float = Field(alias="pClosing")
    final:float = Field(alias="pClosingNotAdjusted")

    @field_validator("date", mode="before")
    def parse_birthdate(cls, value):
        return dt.datetime.strptime(
            str(value),
            "%Y%m%d"
        ).date()
