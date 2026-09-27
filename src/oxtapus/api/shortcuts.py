# ruff: noqa: RUF002
"""Zero-configuration notebook shortcuts."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date

import polars as pl

from oxtapus.api.client import Client
from oxtapus.progress.reporter import ProgressOption


def asset_history(
    asset: str,
    start: date | str | None = None,
    end: date | str | None = None,
    *,
    progress: ProgressOption = None,
) -> pl.DataFrame:
    """تاریخچهٔ روزانهٔ یک ارز یا سکه را برمی‌گرداند.

    Args:
        asset: نام فارسی یا کد canonical دارایی. مقدارهای مجاز شامل ``دلار``،
            ``دلار نیما``، ``یورو``، ``سکه امامی``، ``نیم‌سکه`` و کدهای متناظر هستند.
        start: تاریخ شروع اختیاری؛ تاریخ شمسی در قالب‌های رایج یا تاریخ میلادی ISO.
        end: تاریخ پایان اختیاری؛ تاریخ شمسی در قالب‌های رایج یا تاریخ میلادی ISO.
        progress: ``True`` برای نمایش پیشرفت، callback برای دریافت رویدادها، یا ``None``.

    Returns:
        دیتافریم Polars مرتب‌شده بر اساس ``trading_date`` با قیمت‌های OHLC ریالی.
    """

    with Client() as client:
        return client.assets.history(asset, start, end, progress=progress)


def daily_prices(
    symbols: Sequence[str],
    start: date | str | None = None,
    end: date | str | None = None,
    *,
    adjusted: bool = False,
    progress: ProgressOption = None,
) -> pl.DataFrame:
    """قیمت روزانهٔ یک یا چند نماد را برمی‌گرداند.

    Args:
        symbols: فهرست نماد، ISIN یا کد ابزار TSETMC.
        start: تاریخ شروع اختیاری؛ شمسی یا میلادی ISO.
        end: تاریخ پایان اختیاری؛ شمسی یا میلادی ISO.
        adjusted: فقط ``False``؛ قیمت تعدیل‌شده تا زمان تأیید منبع ارائه نمی‌شود.
        progress: تنظیم نمایش یا callback پیشرفت.

    Returns:
        دیتافریم Polars شامل OHLC، قیمت آخرین معامله، تعداد، حجم و ارزش معاملات.
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
    """آخرین snapshot بازار را برمی‌گرداند.

    Args:
        instrument_types: نوع ابزارها؛ ``equity``، ``etf`` یا هر دو.
        progress: تنظیم نمایش یا callback پیشرفت.

    Returns:
        دیتافریم Polars با یک ردیف برای هر ابزار موجود در دیده‌بان.
    """

    with Client() as client:
        return client.market.market_watch(instrument_types, progress=progress)


def instrument_search(term: str, *, progress: ProgressOption = None) -> pl.DataFrame:
    """نمادها و ابزارهای منطبق با عبارت جست‌وجو را برمی‌گرداند.

    Args:
        term: نماد یا بخشی از نام ابزار.
        progress: تنظیم نمایش یا callback پیشرفت.

    Returns:
        دیتافریم Polars شامل شناسه‌ها، نماد، نام و طبقه‌بندی بازار.
    """

    with Client() as client:
        return client.instruments.search(term, progress=progress)


def instrument_info(identifier: str, *, progress: ProgressOption = None) -> pl.DataFrame:
    """اطلاعات معاملاتی و ارزش‌گذاری یک ابزار را برمی‌گرداند.

    Args:
        identifier: نماد، ISIN، کد ابزار TSETMC یا شناسهٔ provider.
        progress: تنظیم نمایش یا callback پیشرفت.

    Returns:
        دیتافریم تک‌ردیفی Polars شامل صنعت، EPS، P/E، حدود قیمت و اطلاعات انتشار.
    """

    with Client() as client:
        return client.instruments.info(identifier, progress=progress)


def instrument_identity(identifier: str, *, progress: ProgressOption = None) -> pl.DataFrame:
    """هویت و طبقه‌بندی یک ابزار را برمی‌گرداند.

    Args:
        identifier: نماد یا یکی از شناسه‌های رسمی ابزار.
        progress: تنظیم نمایش یا callback پیشرفت.

    Returns:
        دیتافریم تک‌ردیفی Polars شامل نام، شناسه‌ها، بازار، صنعت و زیرصنعت.
    """

    with Client() as client:
        return client.instruments.identity(identifier, progress=progress)


def quote(identifier: str, *, progress: ProgressOption = None) -> pl.DataFrame:
    """آخرین اطلاعات تابلوی یک ابزار را برمی‌گرداند.

    Args:
        identifier: نماد یا شناسهٔ رسمی ابزار.
        progress: تنظیم نمایش یا callback پیشرفت.

    Returns:
        دیتافریم تک‌ردیفی Polars شامل وضعیت، قیمت‌های روز و جمع معاملات.
    """

    with Client() as client:
        return client.market.quote(identifier, progress=progress)


def market_depth(identifier: str, *, progress: ProgressOption = None) -> pl.DataFrame:
    """سطح‌های فعلی سفارش خرید و فروش یک ابزار را برمی‌گرداند.

    Args:
        identifier: نماد یا شناسهٔ رسمی ابزار.
        progress: تنظیم نمایش یا callback پیشرفت.

    Returns:
        دیتافریم Polars با حداکثر پنج ردیف؛ هر ردیف یک سطح order book است.
    """

    with Client() as client:
        return client.market.market_depth(identifier, progress=progress)


def investor_activity(identifier: str, *, progress: ProgressOption = None) -> pl.DataFrame:
    """آمار فعلی خرید و فروش حقیقی و حقوقی را برمی‌گرداند.

    Args:
        identifier: نماد یا شناسهٔ رسمی ابزار.
        progress: تنظیم نمایش یا callback پیشرفت.

    Returns:
        دیتافریم تک‌ردیفی Polars شامل تعداد و حجم خرید و فروش هر گروه.
    """

    with Client() as client:
        return client.market.investor_activity(identifier, progress=progress)


def board_members(identifier: str, *, progress: ProgressOption = None) -> pl.DataFrame:
    """تاریخچهٔ افشای اعضای هیئت‌مدیره را برمی‌گرداند.

    Args:
        identifier: نماد یا شناسهٔ رسمی ابزار.
        progress: تنظیم نمایش یا callback پیشرفت.

    Returns:
        دیتافریم Polars با یک ردیف برای هر عضو در هر اطلاعیه.
    """

    with Client() as client:
        return client.governance.board_members(identifier, progress=progress)


def option_chain(underlying: str, *, progress: ProgressOption = None) -> pl.DataFrame:
    """زنجیرهٔ اختیار معاملهٔ یک دارایی پایه را برمی‌گرداند.

    Args:
        underlying: نماد یا شناسهٔ دارایی پایه.
        progress: تنظیم نمایش یا callback پیشرفت.

    Returns:
        دیتافریم Polars شامل قراردادهای خرید و فروش، سررسید و قیمت اعمال.
    """

    with Client() as client:
        return client.market.option_chain(underlying, progress=progress)
