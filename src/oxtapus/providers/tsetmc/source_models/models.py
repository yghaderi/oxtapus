"""Tolerant source models that preserve and report additive fields."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SourceModel(BaseModel):
    """Allow additive source fields so drift can be reported explicitly."""

    model_config = ConfigDict(extra="allow")

    def unknown_fields(self) -> tuple[str, ...]:
        """Return additive fields observed by Pydantic."""

        return tuple(sorted((self.model_extra or {}).keys()))


class InstrumentSearchSource(SourceModel):
    insCode: str
    lVal30: str
    lVal18AFC: str
    flow: int
    cIsin: str | None = None
    instrumentID: str | None = None
    cgrValCot: str | None = None
    lastDate: int | None = None
    flowTitle: str | None = None
    cgrValCotTitle: str | None = None


class InstrumentInfoSource(SourceModel):
    insCode: str
    lVal30: str
    lVal18AFC: str
    cIsin: str | None = None
    instrumentID: str | None = None
    flow: int | None = None
    flowTitle: str | None = None
    cgrValCot: str | None = None
    cgrValCotTitle: str | None = None
    lastDate: int | None = None
    sector: dict[str, Any] | None = None


class DailyPriceSource(SourceModel):
    insCode: str
    dEven: int
    hEven: int | None = None
    priceFirst: int | None = None
    priceMax: int | None = None
    priceMin: int | None = None
    pClosing: int | None = None
    pDrCotVal: int | None = None
    priceYesterday: int | None = None
    priceChange: float | None = None
    zTotTran: int | None = None
    qTotTran5J: int | None = None
    qTotCap: int | None = None


class OrderBookLevelSource(SourceModel):
    n: int
    qmd: int | None = None
    zmd: int | None = None
    pmd: int | None = None
    pmo: int | None = None
    zmo: int | None = None
    qmo: int | None = None


class MarketWatchSource(SourceModel):
    insCode: str
    insID: str | None = None
    lva: str
    lvc: str
    eps: float | None = None
    pe: str | float | None = None
    pf: int | None = None
    pmx: int | None = None
    pmn: int | None = None
    pdv: int | None = None
    pcl: int | None = None
    py: int | None = None
    pc: int | None = None
    ztt: int | None = None
    qtj: int | None = None
    qtc: int | None = None
    pMax: int | None = None
    pMin: int | None = None
    ztd: int | None = None
    bv: int | None = None
    hEven: int | None = None
    blDs: list[OrderBookLevelSource] = Field(default_factory=list)


class OptionPairSource(SourceModel):
    insCode_P: str
    insCode_C: str
    contractSize: int
    uaInsCode: str
    lVal18AFC_P: str
    lVal30_P: str
    zTotTran_P: int | None = None
    qTotTran5J_P: int | None = None
    qTotCap_P: int | None = None
    pClosing_P: int | None = None
    priceYesterday_P: int | None = None
    oP_P: int | None = None
    pDrCotVal_P: int | None = None
    lval30_UA: str
    beginDate: str | None = None
    endDate: str
    strikePrice: int
    remainedDay: int | None = None
    pDrCotVal_C: int | None = None
    oP_C: int | None = None
    pClosing_C: int | None = None
    priceYesterday_C: int | None = None
    qTotCap_C: int | None = None
    qTotTran5J_C: int | None = None
    zTotTran_C: int | None = None
    lVal30_C: str
    lVal18AFC_C: str
    pMeDem_P: int | None = None
    qTitMeDem_P: int | None = None
    pMeOf_P: int | None = None
    qTitMeOf_P: int | None = None
    pMeDem_C: int | None = None
    qTitMeDem_C: int | None = None
    pMeOf_C: int | None = None
    qTitMeOf_C: int | None = None
