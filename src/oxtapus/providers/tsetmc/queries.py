"""Strict TSETMC query models."""

from datetime import date

from pydantic import Field, field_validator

from oxtapus.domain.identifiers import normalize_persian
from oxtapus.providers.base import QueryModel


class InstrumentSearchQuery(QueryModel):
    """Search instruments by a user-entered term."""

    term: str = Field(min_length=1, max_length=120)

    @field_validator("term")
    @classmethod
    def normalize_term(cls, value: str) -> str:
        result = normalize_persian(value)
        if not result:
            raise ValueError("Search terms cannot be empty.")
        return result


class InstrumentInfoQuery(QueryModel):
    """Fetch one instrument by TSETMC instrument code."""

    tsetmc_instrument_code: str = Field(pattern=r"^[0-9]{5,20}$")


class DailyPriceQuery(QueryModel):
    """Fetch daily prices for one already-resolved instrument."""

    tsetmc_instrument_code: str = Field(pattern=r"^[0-9]{5,20}$")
    symbol: str
    isin: str | None = None
    start: date | None = None
    end: date | None = None

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        return normalize_persian(value)


class MarketWatchQuery(QueryModel):
    """Fetch a market snapshot for canonical instrument types."""

    instrument_types: tuple[str, ...] = ("equity", "etf")


class QuoteQuery(QueryModel):
    """Fetch the latest board quote for one resolved instrument."""

    tsetmc_instrument_code: str = Field(pattern=r"^[0-9]{5,20}$")
    symbol: str

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        return normalize_persian(value)


class OrderBookQuery(QueryModel):
    """Fetch the latest order-book levels for one resolved instrument."""

    tsetmc_instrument_code: str = Field(pattern=r"^[0-9]{5,20}$")


class InvestorActivityQuery(QueryModel):
    """Fetch the latest individual/institutional activity for one instrument."""

    tsetmc_instrument_code: str = Field(pattern=r"^[0-9]{5,20}$")
    symbol: str

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        return normalize_persian(value)


class InstrumentIdentityQuery(QueryModel):
    """Fetch source identity and classification for one resolved instrument."""

    tsetmc_instrument_code: str = Field(pattern=r"^[0-9]{5,20}$")


class BoardMembersQuery(QueryModel):
    """Fetch board-member disclosures for one resolved instrument."""

    tsetmc_instrument_code: str = Field(pattern=r"^[0-9]{5,20}$")
    symbol: str

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        return normalize_persian(value)


class OptionChainQuery(QueryModel):
    """Fetch the option chain for one underlying instrument."""

    underlying_symbol: str
    underlying_tsetmc_instrument_code: str = Field(pattern=r"^[0-9]{5,20}$")

    @field_validator("underlying_symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        return normalize_persian(value)
