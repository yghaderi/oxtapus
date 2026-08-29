"""Zero-configuration notebook shortcuts."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date

import polars as pl

from oxtapus.api.client import Client
from oxtapus.progress.reporter import ProgressOption


def daily_prices(
    symbols: Sequence[str],
    start: date | str | None = None,
    end: date | str | None = None,
    *,
    adjusted: bool = False,
    progress: ProgressOption = None,
) -> pl.DataFrame:
    """Fetch canonical daily prices using a short-lived pooled client."""

    with Client() as client:
        return client.market.daily_prices(
            symbols,
            start,
            end,
            adjusted=adjusted,
            progress=progress,
        )


def market_watch(
    instrument_types: Sequence[str] = ("equity", "etf"),
    *,
    progress: ProgressOption = None,
) -> pl.DataFrame:
    """Fetch a canonical market snapshot using safe defaults."""

    with Client() as client:
        return client.market.market_watch(instrument_types, progress=progress)


def instrument_search(term: str, *, progress: ProgressOption = None) -> pl.DataFrame:
    """Search canonical instruments using safe defaults."""

    with Client() as client:
        return client.instruments.search(term, progress=progress)


def option_chain(underlying: str, *, progress: ProgressOption = None) -> pl.DataFrame:
    """Fetch a canonical option chain using safe defaults."""

    with Client() as client:
        return client.market.option_chain(underlying, progress=progress)
