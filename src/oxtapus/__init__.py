"""Oxtapus: typed, Polars-native Iranian market data."""

from oxtapus import tgju, tsetmc
from oxtapus._version import __version__
from oxtapus.api.async_client import AsyncClient
from oxtapus.api.client import Client
from oxtapus.api.results import FetchResult
from oxtapus.api.settings import Settings
from oxtapus.domain.enums import DataLayer

__all__ = [
    "AsyncClient",
    "Client",
    "DataLayer",
    "FetchResult",
    "Settings",
    "__version__",
    "tgju",
    "tsetmc",
]
