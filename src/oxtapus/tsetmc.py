"""TSETMC-qualified notebook API."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date

import polars as pl

from oxtapus.api.client import Client
from oxtapus.progress.reporter import ProgressOption

__all__ = [
    "board_members",
    "daily_prices",
    "instrument_identity",
    "instrument_info",
    "instrument_search",
    "investor_activity",
    "market_depth",
    "market_watch",
    "option_chain",
    "quote",
]


def daily_prices(
    symbols: Sequence[str],
    start: date | str | None = None,
    end: date | str | None = None,
    *,
    adjusted: bool = False,
    progress: ProgressOption = None,
) -> pl.DataFrame:
    """داده‌های تاریخی معاملهٔ یک یا چند نماد را برمی‌گرداند.

    Args:
        symbols: Symbols, ISINs, or TSETMC instrument codes.
        start: Optional inclusive Jalali or Gregorian start date.
        end: Optional inclusive Jalali or Gregorian end date.
        adjusted: Must be ``False``; adjusted prices are not currently provided.
        progress: Progress reporting configuration or event callback.

    Returns:
        A Polars DataFrame containing canonical daily price rows.
    """

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
    """داده‌های دیده‌بان بازار را برای بخش‌های درخواستی برمی‌گرداند.

    Args:
        instrument_types: Instrument categories to include. Supported values are
            ``equity`` and ``etf``.
        progress: Progress reporting configuration or event callback.

    Returns:
        A Polars DataFrame containing the latest canonical market snapshot.
    """

    with Client() as client:
        return client.market.market_watch(instrument_types, progress=progress)


def instrument_search(term: str, *, progress: ProgressOption = None) -> pl.DataFrame:
    """کد و مشخصات ابزارهای منطبق با عبارت جست‌وجو را برمی‌گرداند.

    Args:
        term: A symbol or instrument-name fragment.
        progress: Progress reporting configuration or event callback.

    Returns:
        A Polars DataFrame containing every matching TSETMC instrument.
    """

    with Client() as client:
        return client.instruments.search(term, progress=progress)


def instrument_info(identifier: str, *, progress: ProgressOption = None) -> pl.DataFrame:
    """داده‌های پایهٔ نماد یا ابزار معاملاتی را برمی‌گرداند.

    Args:
        identifier: A symbol, ISIN, TSETMC instrument code, or provider identifier.
        progress: Progress reporting configuration or event callback.

    Returns:
        A one-row Polars DataFrame containing the instrument information returned by
        TSETMC.
    """

    with Client() as client:
        return client.instruments.info(identifier, progress=progress)


def instrument_identity(identifier: str, *, progress: ProgressOption = None) -> pl.DataFrame:
    """شناسهٔ نماد یا ابزار معاملاتی را برمی‌گرداند.

    Args:
        identifier: A symbol, ISIN, TSETMC instrument code, or provider identifier.
        progress: Progress reporting configuration or event callback.

    Returns:
        A one-row Polars DataFrame containing the instrument identity returned by
        TSETMC.
    """

    with Client() as client:
        return client.instruments.identity(identifier, progress=progress)


def quote(identifier: str, *, progress: ProgressOption = None) -> pl.DataFrame:
    """داده‌های صفحهٔ نماد را برمی‌گرداند.

    Args:
        identifier: A symbol, ISIN, TSETMC instrument code, or provider identifier.
        progress: Progress reporting configuration or event callback.

    Returns:
        A one-row Polars DataFrame containing the latest trading-board data.
    """

    with Client() as client:
        return client.market.quote(identifier, progress=progress)


def market_depth(identifier: str, *, progress: ProgressOption = None) -> pl.DataFrame:
    """سفارش‌های فعلی نماد را برمی‌گرداند.

    Args:
        identifier: A symbol, ISIN, TSETMC instrument code, or provider identifier.
        progress: Progress reporting configuration or event callback.

    Returns:
        A Polars DataFrame containing up to five current bid and ask levels.
    """

    with Client() as client:
        return client.market.market_depth(identifier, progress=progress)


def investor_activity(identifier: str, *, progress: ProgressOption = None) -> pl.DataFrame:
    """داده‌های خرید و فروش حقیقی و حقوقی نماد را برمی‌گرداند.

    Args:
        identifier: A symbol, ISIN, TSETMC instrument code, or provider identifier.
        progress: Progress reporting configuration or event callback.

    Returns:
        A one-row Polars DataFrame containing individual and institutional trading
        activity.
    """

    with Client() as client:
        return client.market.investor_activity(identifier, progress=progress)


def board_members(identifier: str, *, progress: ProgressOption = None) -> pl.DataFrame:
    """اطلاعات اعضای هیئت‌مدیرهٔ شرکت را برمی‌گرداند.

    Args:
        identifier: A symbol, ISIN, TSETMC instrument code, or provider identifier.
        progress: Progress reporting configuration or event callback.

    Returns:
        A Polars DataFrame containing the company's board-member disclosure records.
    """

    with Client() as client:
        return client.governance.board_members(identifier, progress=progress)


def option_chain(underlying: str, *, progress: ProgressOption = None) -> pl.DataFrame:
    """داده‌های نمای بازار اختیار معامله را برمی‌گرداند.

    Args:
        underlying: An underlying symbol, ISIN, or TSETMC instrument code.
        progress: Progress reporting configuration or event callback.

    Returns:
        A Polars DataFrame containing one canonical row per matching option contract.
    """

    with Client() as client:
        return client.market.option_chain(underlying, progress=progress)
