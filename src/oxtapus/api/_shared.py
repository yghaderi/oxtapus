"""Shared public-API validation helpers."""

from __future__ import annotations

import re
from collections.abc import Sequence
from datetime import date

import jdatetime

from oxtapus.domain.errors import UnsupportedCapabilityError
from oxtapus.domain.identifiers import normalize_persian

_DATE_PATTERN = re.compile(
    r"^(?P<year>\d{4})(?:(?P<separator>[-/.])(?P<month>\d{1,2})(?P=separator)"
    r"(?P<day>\d{1,2})|(?P<compact>\d{4}))$"
)
_DATE_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
_DATE_FORMATS = "YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD, or YYYYMMDD"


def parse_date(value: date | str | None, name: str) -> date | None:
    """Parse a Jalali user date, or an explicit Gregorian date, into Gregorian form."""

    if value is None or isinstance(value, date):
        return value

    original = value
    normalized = value.strip().translate(_DATE_DIGITS)
    match = _DATE_PATTERN.fullmatch(normalized)
    if match is None:
        raise _invalid_date(name, original)

    year = int(match.group("year"))
    if compact := match.group("compact"):
        month = int(compact[:2])
        day = int(compact[2:])
    else:
        month = int(match.group("month"))
        day = int(match.group("day"))

    try:
        if 1200 <= year <= 1599:
            converted = jdatetime.date(year, month, day).togregorian()
            return date(converted.year, converted.month, converted.day)
        if 1800 <= year <= 2199:
            return date(year, month, day)
    except (TypeError, ValueError) as exc:
        raise _invalid_date(name, original) from exc

    raise _invalid_date(name, original)


def _invalid_date(name: str, value: str) -> ValueError:
    return ValueError(
        f"Invalid {name}={value!r}. Use a valid Jalali date (year 1200-1599) or "
        f"Gregorian date (year 1800-2199) in one of these formats: {_DATE_FORMATS}."
    )


def normalize_symbols(symbols: Sequence[str]) -> tuple[str, ...]:
    """Normalize and deduplicate identifiers while preserving caller order."""

    values = tuple(dict.fromkeys(normalize_persian(item) for item in symbols))
    if not values or any(not item for item in values):
        raise ValueError("symbols must contain at least one non-empty identifier.")
    return values


def require_unadjusted(adjusted: bool) -> None:
    """Fail explicitly because no verified corporate-action source is enabled."""

    if adjusted:
        raise UnsupportedCapabilityError(
            "Adjusted prices are unavailable until a verified corporate-action source is enabled."
        )
