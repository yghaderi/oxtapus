"""TGJU-qualified notebook API."""

from __future__ import annotations

from datetime import date

import polars as pl

from oxtapus.api.client import Client
from oxtapus.progress.reporter import ProgressOption

__all__ = ["daily_prices"]


def daily_prices(
    asset: str,
    start: date | str | None = None,
    end: date | str | None = None,
    *,
    progress: ProgressOption = None,
) -> pl.DataFrame:
    """داده‌های گذشتهٔ یک ارز یا سکه را از TGJU برمی‌گرداند.

    Args:
        asset: A supported Persian asset name or canonical asset code.
        start: Optional inclusive Jalali or Gregorian start date.
        end: Optional inclusive Jalali or Gregorian end date.
        progress: Progress reporting configuration or event callback.

    Returns:
        A Polars DataFrame containing canonical daily OHLC price rows.
    """

    with Client() as client:
        return client.assets.history(asset, start, end, progress=progress)
