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


class EpsSource(SourceModel):
    epsValue: float | None = None
    estimatedEPS: str | int | float | None = None
    sectorPE: float | None = None
    psr: float | None = None


class SectorSource(SourceModel):
    dEven: int | None = None
    cSecVal: str | None = None
    lSecVal: str | None = None


class StaticThresholdSource(SourceModel):
    insCode: str | None = None
    dEven: int | None = None
    hEven: int | None = None
    psGelStaMax: int | None = None
    psGelStaMin: int | None = None


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
    eps: EpsSource | None = None
    sector: SectorSource | None = None
    staticThreshold: StaticThresholdSource | None = None
    minWeek: int | None = None
    maxWeek: int | None = None
    minYear: int | None = None
    maxYear: int | None = None
    qTotTran5JAvg: int | None = None
    kAjCapValCpsIdx: str | None = None
    dEven: int | None = None
    topInst: int | None = None
    faraDesc: str | None = None
    contractSize: int | None = None
    nav: float | None = None
    underSupervision: int | None = None
    etfIssuedUnit: int | None = None
    etfUnitDeven: int | None = None
    cValMne: str | None = None
    lVal18: str | None = None
    cSocCSAC: str | None = None
    lSoc30: str | None = None
    yMarNSC: str | None = None
    yVal: str | None = None
    zTitad: int | None = None
    baseVol: int | None = None
    cComVal: str | None = None
    sourceID: int | None = None


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


class BestLimitSource(SourceModel):
    number: int = Field(ge=1, le=5)
    qTitMeDem: int | None = Field(default=None, ge=0)
    zOrdMeDem: int | None = Field(default=None, ge=0)
    pMeDem: int | None = Field(default=None, ge=0)
    pMeOf: int | None = Field(default=None, ge=0)
    zOrdMeOf: int | None = Field(default=None, ge=0)
    qTitMeOf: int | None = Field(default=None, ge=0)
    title: str | None = None
    insCode: str | None = None


class InstrumentStateSource(SourceModel):
    idn: int | None = None
    dEven: int | None = None
    hEven: int | None = None
    insCode: str | None = None
    lVal18AFC: str | None = None
    lVal30: str | None = None
    cEtaval: str | None = None
    realHeven: int | None = None
    underSupervision: int | None = None
    cEtavalTitle: str | None = None


class ClosingPriceInfoSource(SourceModel):
    instrumentState: InstrumentStateSource
    instrument: dict[str, Any] | None = None
    lastHEven: int | None = None
    finalLastDate: int | None = None
    nvt: float | None = None
    mop: int | None = None
    pRedTran: float | None = None
    thirtyDayClosingHistory: Any | None = None
    priceChange: float | None = None
    priceMin: int | None = None
    priceMax: int | None = None
    priceYesterday: int | None = None
    priceFirst: int | None = None
    last: bool | None = None
    id: int | None = None
    insCode: str | None = None
    dEven: int | None = None
    hEven: int | None = None
    pClosing: int | None = None
    iClose: bool | None = None
    yClose: bool | None = None
    pDrCotVal: int | None = None
    zTotTran: int | None = None
    qTotTran5J: int | None = None
    qTotCap: int | None = None


class ClientTypeSource(SourceModel):
    buy_I_Volume: int | None = None
    buy_N_Volume: int | None = None
    buy_DDD_Volume: int | None = None
    buy_CountI: int | None = None
    buy_CountN: int | None = None
    buy_CountDDD: int | None = None
    sell_I_Volume: int | None = None
    sell_N_Volume: int | None = None
    sell_CountI: int | None = None
    sell_CountN: int | None = None


class SubSectorSource(SourceModel):
    dEven: int | None = None
    cSecVal: str | None = None
    cSoSecVal: int | None = None
    lSoSecVal: str | None = None


class InstrumentIdentitySource(SourceModel):
    sector: SectorSource | None = None
    subSector: SubSectorSource | None = None
    cValMne: str | None = None
    lVal18: str | None = None
    cSocCSAC: str | None = None
    lSoc30: str | None = None
    yMarNSC: str | None = None
    yVal: str | None = None
    insCode: str | None = None
    lVal30: str
    lVal18AFC: str
    flow: int | None = None
    cIsin: str | None = None
    zTitad: int | None = None
    baseVol: int | None = None
    instrumentID: str | None = None
    cgrValCot: str | None = None
    cComVal: str | None = None
    lastDate: int | None = None
    sourceID: int | None = None
    flowTitle: str | None = None
    cgrValCotTitle: str | None = None


class BoardStatementSource(SourceModel):
    title: str
    sentDateTime_Gregorian: str
    publishDateTime_Gregorian: str
    publishDateTime_DEven: int
    reportSubType: int
    pageID: int
    content: str


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
