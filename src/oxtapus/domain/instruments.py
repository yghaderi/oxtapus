"""Canonical instrument records."""

from dataclasses import dataclass

from oxtapus.domain.enums import InstrumentState


@dataclass(frozen=True, slots=True)
class Instrument:
    """A provider-independent instrument identity."""

    tsetmc_instrument_code: str
    symbol: str
    instrument_name: str
    isin: str | None = None
    provider_instrument_id: str | None = None
    exchange: str | None = None
    market: str | None = None
    board: str | None = None
    instrument_type: str | None = None
    asset_class: str | None = None
    sector_code: str | None = None
    sector_name: str | None = None
    state: InstrumentState = InstrumentState.UNKNOWN
    source_symbol: str | None = None
    source_name: str | None = None
