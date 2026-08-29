"""Shared public-API validation helpers."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date

from oxtapus.domain.errors import UnsupportedCapabilityError
from oxtapus.domain.identifiers import normalize_persian


def parse_date(value: date | str | None, name: str) -> date | None:
    """Parse ISO Gregorian dates without guessing locale-specific formats."""

    if value is None or isinstance(value, date):
        return value
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an ISO date in YYYY-MM-DD form.") from exc


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
