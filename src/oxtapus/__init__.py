"""Oxtapus: typed, Polars-native Iranian market data."""

from oxtapus._version import __version__
from oxtapus.api.async_client import AsyncClient
from oxtapus.api.client import Client
from oxtapus.api.results import FetchResult
from oxtapus.api.settings import Settings
from oxtapus.api.shortcuts import daily_prices, instrument_search, market_watch, option_chain
from oxtapus.domain.enums import DataLayer

__all__ = [
    "AsyncClient",
    "Client",
    "DataLayer",
    "FetchResult",
    "Settings",
    "__version__",
    "daily_prices",
    "instrument_search",
    "market_watch",
    "option_chain",
]
