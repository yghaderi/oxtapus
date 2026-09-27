"""Strict TGJU query models."""

from datetime import date

from pydantic import field_validator

from oxtapus.providers.base import QueryModel
from oxtapus.providers.tgju.assets import resolve_asset


class AssetPriceHistoryQuery(QueryModel):
    """Fetch complete available daily history for one supported asset."""

    asset: str
    start: date | None = None
    end: date | None = None

    @field_validator("asset")
    @classmethod
    def canonicalize_asset(cls, value: str) -> str:
        return resolve_asset(value).code
