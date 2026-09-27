"""Pure TGJU-to-canonical asset-price transformations."""

from __future__ import annotations

import re
from datetime import date
from typing import Any

import polars as pl
from pydantic import ValidationError

from oxtapus.domain.asset_prices import ASSET_PRICE_COLUMNS
from oxtapus.domain.errors import SchemaValidationError
from oxtapus.providers.base import TransformOutput
from oxtapus.providers.tgju.assets import asset_by_code
from oxtapus.providers.tgju.queries import AssetPriceHistoryQuery
from oxtapus.providers.tgju.source_models import TgjuHistoryEnvelope

_SPAN_PATTERN = re.compile(
    r'^\s*<span\s+class="(?P<direction>high|low)?"\s+dir="ltr">(?P<value>.*?)</span>\s*$',
    re.IGNORECASE,
)
_DIGIT_TRANSLATION = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def transform_asset_price_history(body: object, query: AssetPriceHistoryQuery) -> TransformOutput:
    """Canonicalize a supported TGJU daily price history."""

    try:
        envelope = TgjuHistoryEnvelope.model_validate(body)
    except ValidationError as exc:
        raise SchemaValidationError("TGJU history violates its source contract.") from exc

    asset = asset_by_code(query.asset)
    rows: list[dict[str, object]] = []
    additive_positions: set[str] = set()
    for source_row in envelope.data:
        if len(source_row) < 8:
            raise SchemaValidationError("TGJU history rows must contain at least eight values.")
        if len(source_row) > 8:
            additive_positions.update(f"data[*][{index}]" for index in range(8, len(source_row)))
        trading_date = _parse_date(source_row[6], "gregorian date")
        if query.start is not None and trading_date < query.start:
            continue
        if query.end is not None and trading_date > query.end:
            continue
        change = _parse_directional_number(source_row[4], integral=True)
        change_percentage = _parse_directional_number(source_row[5], integral=False)
        rows.append(
            {
                "asset_code": asset.code,
                "asset_name": asset.name,
                "provider_instrument_id": asset.source_id,
                "trading_date": trading_date,
                "jalali_date": _parse_jalali_date(source_row[7]),
                "open_price": _parse_integral(source_row[0], "open price"),
                "high_price": _parse_integral(source_row[2], "high price"),
                "low_price": _parse_integral(source_row[1], "low price"),
                "close_price": _parse_integral(source_row[3], "close price"),
                "price_change": int(change) if change is not None else None,
                "price_change_percentage": change_percentage,
                "currency": "IRR",
                "unit": asset.unit,
            }
        )
    frame = pl.DataFrame(rows, schema=_schema()).sort("trading_date")
    unknown = set(envelope.unknown_fields()) | additive_positions
    return TransformOutput(
        data=frame.select(ASSET_PRICE_COLUMNS),
        unknown_fields=tuple(sorted(unknown)),
    )


def _parse_integral(value: Any, field: str) -> int | None:
    text = _plain_number(value)
    if text is None:
        return None
    try:
        number = float(text)
    except ValueError as exc:
        raise SchemaValidationError(f"TGJU {field} is not numeric.") from exc
    if not number.is_integer():
        raise SchemaValidationError(f"TGJU {field} is not integral.")
    return int(number)


def _parse_directional_number(value: Any, *, integral: bool) -> float | None:
    if value is None:
        return None
    raw = str(value).translate(_DIGIT_TRANSLATION).strip()
    direction: str | None = None
    match = _SPAN_PATTERN.fullmatch(raw)
    if match:
        matched_direction = match.group("direction")
        direction = matched_direction.lower() if matched_direction else None
        raw = match.group("value").strip()
    text = _plain_number(raw.rstrip("%"))
    if text is None:
        return None
    try:
        number = float(text)
    except ValueError as exc:
        raise SchemaValidationError("TGJU price change is not numeric.") from exc
    if integral and not number.is_integer():
        raise SchemaValidationError("TGJU price change is not integral.")
    if direction == "low":
        return -abs(number)
    if direction == "high":
        return abs(number)
    return number


def _plain_number(value: Any) -> str | None:
    if value is None:
        return None
    result = str(value).translate(_DIGIT_TRANSLATION).replace(",", "").strip()
    return None if result in {"", "-", "—", "null", "None"} else result


def _parse_date(value: Any, field: str) -> date:
    text = str(value).translate(_DIGIT_TRANSLATION).strip().replace("/", "-")
    try:
        return date.fromisoformat(text)
    except ValueError as exc:
        raise SchemaValidationError(f"TGJU {field} is not a valid date.") from exc


def _parse_jalali_date(value: Any) -> str:
    text = str(value).translate(_DIGIT_TRANSLATION).strip().replace("/", "-")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        raise SchemaValidationError("TGJU Jalali date is malformed.")
    return text


def _schema() -> pl.Schema:
    return pl.Schema(
        {
            "asset_code": pl.String,
            "asset_name": pl.String,
            "provider_instrument_id": pl.String,
            "trading_date": pl.Date,
            "jalali_date": pl.String,
            "open_price": pl.Int64,
            "high_price": pl.Int64,
            "low_price": pl.Int64,
            "close_price": pl.Int64,
            "price_change": pl.Int64,
            "price_change_percentage": pl.Float64,
            "currency": pl.String,
            "unit": pl.String,
        }
    )
