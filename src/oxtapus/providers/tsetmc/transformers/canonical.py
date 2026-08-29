"""Pure canonical transformations for verified source schemas."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime, time
from typing import TypeVar
from zoneinfo import ZoneInfo

import polars as pl
from pydantic import ValidationError

from oxtapus.domain.calendar import EXCHANGE_TIMEZONE
from oxtapus.domain.errors import SchemaValidationError
from oxtapus.domain.identifiers import normalize_persian
from oxtapus.providers.base import TransformOutput
from oxtapus.providers.tsetmc.queries import (
    DailyPriceQuery,
    MarketWatchQuery,
    OptionChainQuery,
)
from oxtapus.providers.tsetmc.source_models import (
    DailyPriceSource,
    InstrumentInfoSource,
    InstrumentSearchSource,
    MarketWatchSource,
    OptionPairSource,
    SourceModel,
)

S = TypeVar("S", bound=SourceModel)


def transform_instrument_search(records: list[dict[str, object]]) -> TransformOutput:
    """Canonicalize instrument search results while preserving source display strings."""

    models = _validate_many(InstrumentSearchSource, records)
    rows = [
        {
            "tsetmc_instrument_code": item.insCode,
            "symbol": normalize_persian(item.lVal18AFC),
            "instrument_name": normalize_persian(item.lVal30),
            "source_symbol": item.lVal18AFC,
            "source_name": item.lVal30,
            "isin": item.cIsin,
            "provider_instrument_id": item.instrumentID,
            "exchange": _exchange(item.flow),
            "market": item.flowTitle,
            "board": item.cgrValCotTitle,
            "board_code": item.cgrValCot,
            "instrument_type": _instrument_type(item.cgrValCot),
            "state": "active" if item.lastDate == 1 else "unknown",
        }
        for item in models
    ]
    return TransformOutput(
        data=pl.DataFrame(rows),
        unknown_fields=_unknown_fields(models),
    )


def transform_instrument_info(record: dict[str, object]) -> TransformOutput:
    """Canonicalize one fully identified instrument."""

    try:
        item = InstrumentInfoSource.model_validate(record)
    except ValidationError as exc:
        raise SchemaValidationError("Instrument info violates its source contract.") from exc
    sector = item.sector or {}
    row = {
        "tsetmc_instrument_code": item.insCode,
        "symbol": normalize_persian(item.lVal18AFC),
        "instrument_name": normalize_persian(item.lVal30),
        "source_symbol": item.lVal18AFC,
        "source_name": item.lVal30,
        "isin": item.cIsin,
        "provider_instrument_id": item.instrumentID,
        "exchange": _exchange(item.flow),
        "market": item.flowTitle,
        "board": item.cgrValCotTitle,
        "board_code": item.cgrValCot,
        "instrument_type": _instrument_type(item.cgrValCot),
        "sector_code": _optional_string(sector.get("cSecVal")),
        "sector_name": _optional_string(sector.get("lSecVal")),
        "state": "active" if item.lastDate == 1 else "unknown",
    }
    return TransformOutput(data=pl.DataFrame([row]), unknown_fields=item.unknown_fields())


def transform_daily_prices(
    records: list[dict[str, object]], query: DailyPriceQuery
) -> TransformOutput:
    """Canonicalize daily OHLCV with exact integral types and null preservation."""

    models = _validate_many(DailyPriceSource, records)
    rows: list[dict[str, object]] = []
    for item in models:
        trading_date = _parse_yyyymmdd(item.dEven, "dEven")
        if query.start is not None and trading_date < query.start:
            continue
        if query.end is not None and trading_date > query.end:
            continue
        rows.append(
            {
                "isin": query.isin,
                "symbol": query.symbol,
                "tsetmc_instrument_code": item.insCode,
                "trading_date": trading_date,
                "open_price": item.priceFirst,
                "high_price": item.priceMax,
                "low_price": item.priceMin,
                "close_price": item.pClosing,
                "last_price": item.pDrCotVal,
                "previous_close_price": item.priceYesterday,
                "price_change": item.priceChange,
                "trade_count": item.zTotTran,
                "trade_volume": item.qTotTran5J,
                "trade_value": item.qTotCap,
            }
        )
    frame = pl.DataFrame(rows, schema=_daily_schema()) if rows else _empty_daily_prices()
    if frame.height:
        frame = frame.unique(subset=["tsetmc_instrument_code", "trading_date"], keep="last").sort(
            ["tsetmc_instrument_code", "trading_date"]
        )
    return TransformOutput(data=frame, unknown_fields=_unknown_fields(models))


def transform_market_watch(
    records: list[dict[str, object]], query: MarketWatchQuery, retrieved_at: datetime
) -> TransformOutput:
    """Canonicalize verified compact market-watch fields."""

    models = _validate_many(MarketWatchSource, records)
    local_date = retrieved_at.astimezone(ZoneInfo(EXCHANGE_TIMEZONE)).date()
    rows: list[dict[str, object]] = []
    for item in models:
        event_timestamp = _event_timestamp(local_date, item.hEven)
        instrument_type = "etf" if (item.insID or "").startswith("IRT") else "equity"
        if instrument_type not in query.instrument_types:
            continue
        rows.append(
            {
                "provider_instrument_id": item.insID,
                "symbol": normalize_persian(item.lva),
                "instrument_name": normalize_persian(item.lvc),
                "tsetmc_instrument_code": item.insCode,
                "instrument_type": instrument_type,
                "event_timestamp": event_timestamp,
                "open_price": item.pf,
                "high_price": item.pmx,
                "low_price": item.pmn,
                "close_price": item.pcl,
                "last_price": item.pdv,
                "previous_close_price": item.py,
                "price_change": item.pc,
                "trade_count": item.ztt,
                "trade_volume": item.qtj,
                "trade_value": item.qtc,
                "price_limit_upper": item.pMax,
                "price_limit_lower": item.pMin,
                "base_volume": item.bv,
                "shares_outstanding": item.ztd,
                "earnings_per_share": item.eps,
                "price_to_earnings_ratio": _optional_float(item.pe),
                "market_capitalization": (
                    item.pcl * item.ztd if item.pcl is not None and item.ztd is not None else None
                ),
            }
        )
    return TransformOutput(data=pl.DataFrame(rows), unknown_fields=_unknown_fields(models))


def transform_option_chain(
    records: list[dict[str, object]], query: OptionChainQuery
) -> TransformOutput:
    """Flatten paired put/call source records into one row per contract."""

    models = _validate_many(OptionPairSource, records)
    rows: list[dict[str, object]] = []
    for item in models:
        if item.uaInsCode != query.underlying_tsetmc_instrument_code:
            continue
        expiration = _parse_date_text(item.endDate, "endDate")
        rows.extend(
            [
                _option_row(item, query, expiration, "put"),
                _option_row(item, query, expiration, "call"),
            ]
        )
    frame = pl.DataFrame(rows)
    if frame.height:
        frame = frame.unique(subset=["tsetmc_instrument_code"], keep="last").sort(
            ["expiration_date", "strike_price", "option_type"]
        )
    return TransformOutput(data=frame, unknown_fields=_unknown_fields(models))


def _option_row(
    item: OptionPairSource,
    query: OptionChainQuery,
    expiration: date,
    option_type: str,
) -> dict[str, object]:
    suffix = "P" if option_type == "put" else "C"
    return {
        "underlying_symbol": query.underlying_symbol,
        "underlying_tsetmc_instrument_code": item.uaInsCode,
        "option_type": option_type,
        "option_style": None,
        "symbol": normalize_persian(getattr(item, f"lVal18AFC_{suffix}")),
        "instrument_name": normalize_persian(getattr(item, f"lVal30_{suffix}")),
        "tsetmc_instrument_code": getattr(item, f"insCode_{suffix}"),
        "strike_price": item.strikePrice,
        "expiration_date": expiration,
        "days_to_expiration": item.remainedDay,
        "contract_multiplier": item.contractSize,
        "open_interest": getattr(item, f"oP_{suffix}"),
        "close_price": getattr(item, f"pClosing_{suffix}"),
        "last_price": getattr(item, f"pDrCotVal_{suffix}"),
        "previous_close_price": getattr(item, f"priceYesterday_{suffix}"),
        "trade_count": getattr(item, f"zTotTran_{suffix}"),
        "trade_volume": getattr(item, f"qTotTran5J_{suffix}"),
        "trade_value": getattr(item, f"qTotCap_{suffix}"),
        "bid_price": getattr(item, f"pMeDem_{suffix}"),
        "bid_size": getattr(item, f"qTitMeDem_{suffix}"),
        "ask_price": getattr(item, f"pMeOf_{suffix}"),
        "ask_size": getattr(item, f"qTitMeOf_{suffix}"),
    }


def _validate_many(model: type[S], records: list[dict[str, object]]) -> list[S]:
    try:
        return [model.model_validate(record) for record in records]
    except ValidationError as exc:
        raise SchemaValidationError(f"{model.__name__} violates its source contract.") from exc


def _unknown_fields(models: Sequence[SourceModel]) -> tuple[str, ...]:
    values: set[str] = set()
    for model in models:
        values.update(model.unknown_fields())
    return tuple(sorted(values))


def _daily_schema() -> pl.Schema:
    return pl.Schema(
        {
            "isin": pl.String,
            "symbol": pl.String,
            "tsetmc_instrument_code": pl.String,
            "trading_date": pl.Date,
            "open_price": pl.Int64,
            "high_price": pl.Int64,
            "low_price": pl.Int64,
            "close_price": pl.Int64,
            "last_price": pl.Int64,
            "previous_close_price": pl.Int64,
            "price_change": pl.Float64,
            "trade_count": pl.Int64,
            "trade_volume": pl.Int64,
            "trade_value": pl.Int64,
        }
    )


def _empty_daily_prices() -> pl.DataFrame:
    return pl.DataFrame(schema=_daily_schema())


def _parse_yyyymmdd(value: int, field: str) -> date:
    return _parse_date_text(str(value), field)


def _parse_date_text(value: str, field: str) -> date:
    try:
        return date.fromisoformat(f"{value[:4]}-{value[4:6]}-{value[6:]}")
    except ValueError as exc:
        raise SchemaValidationError(
            f"Source field {field!r} is not a valid YYYYMMDD date."
        ) from exc


def _event_timestamp(local_date: date, value: int | None) -> datetime | None:
    if value is None:
        return None
    padded = f"{value:06d}"
    try:
        local_time = time(int(padded[:2]), int(padded[2:4]), int(padded[4:]))
    except ValueError as exc:
        raise SchemaValidationError("hEven is not a valid HHMMSS time.") from exc
    return datetime.combine(local_date, local_time, tzinfo=ZoneInfo(EXCHANGE_TIMEZONE))


def _exchange(flow: int | None) -> str | None:
    if flow is None:
        return None
    return {1: "Tehran Stock Exchange", 2: "Iran Fara Bourse"}.get(flow)


def _instrument_type(board_code: str | None) -> str | None:
    if board_code in {"N1", "N2", "Z1", "OT"}:
        return "equity"
    if board_code in {"5A", "51", "52", "53", "54", "55", "56", "57", "58", "H1"}:
        return "etf"
    if board_code == "17":
        return "debt"
    return None


def _optional_string(value: object) -> str | None:
    return str(value) if value is not None else None


def _optional_float(value: str | float | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, str) and value.strip().lower() in {"", "-", "—", "null"}:
        return None
    try:
        return float(value)
    except ValueError as exc:
        raise SchemaValidationError("price-to-earnings ratio is malformed.") from exc
