"""Exchange calendar constants."""

from __future__ import annotations

from datetime import date

EXCHANGE_TIMEZONE = "Asia/Tehran"
TRADING_CALENDAR_COLUMNS = (
    "trading_date",
    "exchange",
    "is_trading_day",
    "session_open",
    "session_close",
)


def gregorian_to_jalali(value: date) -> tuple[int, int, int]:
    """Convert a Gregorian date to a Jalali year, month, and day tuple."""

    gregorian_days = (
        365 * (value.year - 1600)
        + (value.year - 1600 + 3) // 4
        - (value.year - 1600 + 99) // 100
        + (value.year - 1600 + 399) // 400
    )
    month_days = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    gregorian_days += sum(month_days[: value.month - 1]) + value.day - 1
    leap = value.year % 400 == 0 or (value.year % 4 == 0 and value.year % 100 != 0)
    if value.month > 2 and leap:
        gregorian_days += 1
    jalali_days = gregorian_days - 79
    cycles, remainder = divmod(jalali_days, 12053)
    jalali_year = 979 + 33 * cycles + 4 * (remainder // 1461)
    remainder %= 1461
    if remainder >= 366:
        jalali_year += (remainder - 1) // 365
        remainder = (remainder - 1) % 365
    if remainder < 186:
        jalali_month, jalali_day = divmod(remainder, 31)
        return jalali_year, jalali_month + 1, jalali_day + 1
    jalali_month, jalali_day = divmod(remainder - 186, 30)
    return jalali_year, jalali_month + 7, jalali_day + 1
