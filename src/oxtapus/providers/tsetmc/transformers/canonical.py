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
from oxtapus.domain.investor_activity import INVESTOR_ACTIVITY_COLUMNS
from oxtapus.domain.order_books import ORDER_BOOK_COLUMNS
from oxtapus.domain.prices import QUOTE_COLUMNS
from oxtapus.providers.base import TransformOutput
from oxtapus.providers.tsetmc.queries import (
    DailyPriceQuery,
    InstrumentIdentityQuery,
    InvestorActivityQuery,
    MarketWatchQuery,
    OptionChainQuery,
    OrderBookQuery,
    QuoteQuery,
)
from oxtapus.providers.tsetmc.source_models import (
    BestLimitSource,
    ClientTypeSource,
    ClosingPriceInfoSource,
    DailyPriceSource,
    InstrumentIdentitySource,
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
    sector = item.sector
    eps = item.eps
    threshold = item.staticThreshold
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
        "sector_code": _optional_string(sector.cSecVal if sector else None),
        "sector_name": _optional_string(sector.lSecVal if sector else None),
        "state": "active" if item.lastDate == 1 else "unknown",
        "earnings_per_share": eps.epsValue if eps else None,
        "estimated_earnings_per_share": _optional_integral(
            eps.estimatedEPS if eps else None,
            "estimatedEPS",
        ),
        "sector_price_to_earnings_ratio": eps.sectorPE if eps else None,
        "price_to_sales_ratio": eps.psr if eps else None,
        "price_limit_upper": threshold.psGelStaMax if threshold else None,
        "price_limit_lower": threshold.psGelStaMin if threshold else None,
        "weekly_low_price": item.minWeek,
        "weekly_high_price": item.maxWeek,
        "yearly_low_price": item.minYear,
        "yearly_high_price": item.maxYear,
        "average_trade_volume": item.qTotTran5JAvg,
        "contract_size": item.contractSize,
        "net_asset_value": item.nav,
        "under_supervision": _optional_bool_flag(
            item.underSupervision,
            "underSupervision",
        ),
        "etf_issued_units": item.etfIssuedUnit,
        "shares_outstanding": item.zTitad,
        "base_volume": item.baseVol,
    }
    nested_unknown: set[str] = set()
    if eps:
        nested_unknown.update(f"eps.{field}" for field in eps.unknown_fields())
    if sector:
        nested_unknown.update(f"sector.{field}" for field in sector.unknown_fields())
    if threshold:
        nested_unknown.update(f"staticThreshold.{field}" for field in threshold.unknown_fields())
    return TransformOutput(
        data=pl.DataFrame([row], schema=_instrument_info_schema()),
        unknown_fields=tuple(sorted(set(item.unknown_fields()) | nested_unknown)),
    )


def transform_instrument_identity(
    record: dict[str, object], query: InstrumentIdentityQuery
) -> TransformOutput:
    """Canonicalize source identity while trusting the query-owned instrument code."""

    try:
        item = InstrumentIdentitySource.model_validate(record)
    except ValidationError as exc:
        raise SchemaValidationError("Instrument identity violates its source contract.") from exc
    sector = item.sector
    subsector = item.subSector
    row = {
        "tsetmc_instrument_code": query.tsetmc_instrument_code,
        "symbol": normalize_persian(item.lVal18AFC),
        "instrument_name": normalize_persian(item.lVal30),
        "source_symbol": item.lVal18AFC,
        "source_name": item.lVal30,
        "isin": item.cIsin,
        "provider_instrument_id": item.instrumentID,
        "exchange": _exchange(item.flow),
        "market": _optional_string(item.flowTitle),
        "board": _optional_string(item.cgrValCotTitle),
        "board_code": _optional_string(item.cgrValCot),
        "instrument_type": _instrument_type(item.cgrValCot),
        "sector_code": _optional_string(sector.cSecVal if sector else None),
        "sector_name": _optional_string(sector.lSecVal if sector else None),
        "subsector_code": _optional_string(subsector.cSoSecVal if subsector else None),
        "subsector_name": _optional_string(subsector.lSoSecVal if subsector else None),
        "company_code": _optional_string(item.cSocCSAC),
        "company_name": _optional_string(item.lSoc30),
        "latin_name": _optional_string(item.lVal18),
        "currency_code": _optional_string(item.cValMne),
        "state": "active" if item.lastDate == 1 else "unknown",
    }
    nested_unknown: set[str] = set()
    if sector:
        nested_unknown.update(f"sector.{field}" for field in sector.unknown_fields())
    if subsector:
        nested_unknown.update(f"subSector.{field}" for field in subsector.unknown_fields())
    return TransformOutput(
        data=pl.DataFrame([row], schema=_instrument_identity_schema()),
        unknown_fields=tuple(sorted(set(item.unknown_fields()) | nested_unknown)),
    )


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


def transform_quote(record: dict[str, object], query: QuoteQuery) -> TransformOutput:
    """Canonicalize the latest per-instrument board quote."""

    try:
        item = ClosingPriceInfoSource.model_validate(record)
    except ValidationError as exc:
        raise SchemaValidationError("Closing-price info violates its source contract.") from exc
    trading_date = _optional_source_date(item.dEven or item.finalLastDate, "dEven")
    row = {
        "tsetmc_instrument_code": query.tsetmc_instrument_code,
        "symbol": query.symbol,
        "trading_date": trading_date,
        "event_timestamp": _optional_event_timestamp(trading_date, item.hEven),
        "last_event_timestamp": _optional_event_timestamp(trading_date, item.lastHEven),
        "trading_state_code": _optional_string(item.instrumentState.cEtaval),
        "trading_state": _optional_string(item.instrumentState.cEtavalTitle),
        "under_supervision": _optional_bool_flag(
            item.instrumentState.underSupervision,
            "instrumentState.underSupervision",
        ),
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
    frame = pl.DataFrame([row], schema=_quote_schema())
    nested_unknown = {f"instrumentState.{field}" for field in item.instrumentState.unknown_fields()}
    return TransformOutput(
        data=frame.select(QUOTE_COLUMNS),
        unknown_fields=tuple(sorted(set(item.unknown_fields()) | nested_unknown)),
    )


def transform_order_book(
    records: list[dict[str, object]], query: OrderBookQuery, retrieved_at: datetime
) -> TransformOutput:
    """Canonicalize up to five best bid/ask levels without inventing missing values."""

    models = _validate_many(BestLimitSource, records)
    levels = [item.number for item in models]
    if len(levels) != len(set(levels)):
        raise SchemaValidationError("Order-book levels must be unique.")
    for item in models:
        if item.insCode not in {None, query.tsetmc_instrument_code}:
            raise SchemaValidationError("Order-book instrument code does not match the query.")
    rows = [
        {
            "tsetmc_instrument_code": query.tsetmc_instrument_code,
            "event_timestamp": retrieved_at,
            "order_book_level": item.number,
            "bid_price": item.pMeDem,
            "bid_size": item.qTitMeDem,
            "bid_order_count": item.zOrdMeDem,
            "ask_price": item.pMeOf,
            "ask_size": item.qTitMeOf,
            "ask_order_count": item.zOrdMeOf,
        }
        for item in models
    ]
    frame = (
        pl.DataFrame(rows, schema=_order_book_schema()).sort("order_book_level")
        if rows
        else pl.DataFrame(schema=_order_book_schema())
    )
    return TransformOutput(
        data=frame.select(ORDER_BOOK_COLUMNS),
        unknown_fields=_unknown_fields(models),
    )


def transform_investor_activity(
    record: dict[str, object], query: InvestorActivityQuery, retrieved_at: datetime
) -> TransformOutput:
    """Canonicalize individual and institutional buy/sell activity."""

    try:
        item = ClientTypeSource.model_validate(record)
    except ValidationError as exc:
        raise SchemaValidationError("Client-type data violates its source contract.") from exc
    row = {
        "tsetmc_instrument_code": query.tsetmc_instrument_code,
        "symbol": query.symbol,
        "event_timestamp": retrieved_at,
        "individual_buy_count": item.buy_CountI,
        "individual_buy_volume": item.buy_I_Volume,
        "individual_buy_value": None,
        "individual_sell_count": item.sell_CountI,
        "individual_sell_volume": item.sell_I_Volume,
        "individual_sell_value": None,
        "institutional_buy_count": item.buy_CountN,
        "institutional_buy_volume": item.buy_N_Volume,
        "institutional_buy_value": None,
        "institutional_sell_count": item.sell_CountN,
        "institutional_sell_volume": item.sell_N_Volume,
        "institutional_sell_value": None,
    }
    frame = pl.DataFrame([row], schema=_investor_activity_schema())
    warnings: tuple[str, ...] = (
        "The source does not report buy/sell values; canonical value columns remain null.",
    )
    if item.buy_DDD_Volume not in {None, 0} or item.buy_CountDDD not in {None, 0}:
        warnings += ("The source reported an unclassified DDD buyer category.",)
    return TransformOutput(
        data=frame.select(INVESTOR_ACTIVITY_COLUMNS),
        warnings=warnings,
        unknown_fields=item.unknown_fields(),
    )


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


def _instrument_info_schema() -> pl.Schema:
    return pl.Schema(
        {
            "tsetmc_instrument_code": pl.String,
            "symbol": pl.String,
            "instrument_name": pl.String,
            "source_symbol": pl.String,
            "source_name": pl.String,
            "isin": pl.String,
            "provider_instrument_id": pl.String,
            "exchange": pl.String,
            "market": pl.String,
            "board": pl.String,
            "board_code": pl.String,
            "instrument_type": pl.String,
            "sector_code": pl.String,
            "sector_name": pl.String,
            "state": pl.String,
            "earnings_per_share": pl.Float64,
            "estimated_earnings_per_share": pl.Int64,
            "sector_price_to_earnings_ratio": pl.Float64,
            "price_to_sales_ratio": pl.Float64,
            "price_limit_upper": pl.Int64,
            "price_limit_lower": pl.Int64,
            "weekly_low_price": pl.Int64,
            "weekly_high_price": pl.Int64,
            "yearly_low_price": pl.Int64,
            "yearly_high_price": pl.Int64,
            "average_trade_volume": pl.Int64,
            "contract_size": pl.Int64,
            "net_asset_value": pl.Float64,
            "under_supervision": pl.Boolean,
            "etf_issued_units": pl.Int64,
            "shares_outstanding": pl.Int64,
            "base_volume": pl.Int64,
        }
    )


def _instrument_identity_schema() -> pl.Schema:
    return pl.Schema(
        {
            "tsetmc_instrument_code": pl.String,
            "symbol": pl.String,
            "instrument_name": pl.String,
            "source_symbol": pl.String,
            "source_name": pl.String,
            "isin": pl.String,
            "provider_instrument_id": pl.String,
            "exchange": pl.String,
            "market": pl.String,
            "board": pl.String,
            "board_code": pl.String,
            "instrument_type": pl.String,
            "sector_code": pl.String,
            "sector_name": pl.String,
            "subsector_code": pl.String,
            "subsector_name": pl.String,
            "company_code": pl.String,
            "company_name": pl.String,
            "latin_name": pl.String,
            "currency_code": pl.String,
            "state": pl.String,
        }
    )


def _quote_schema() -> pl.Schema:
    return pl.Schema(
        {
            "tsetmc_instrument_code": pl.String(),
            "symbol": pl.String(),
            "trading_date": pl.Date(),
            "event_timestamp": pl.Datetime(time_zone=EXCHANGE_TIMEZONE),
            "last_event_timestamp": pl.Datetime(time_zone=EXCHANGE_TIMEZONE),
            "trading_state_code": pl.String(),
            "trading_state": pl.String(),
            "under_supervision": pl.Boolean(),
            "open_price": pl.Int64(),
            "high_price": pl.Int64(),
            "low_price": pl.Int64(),
            "close_price": pl.Int64(),
            "last_price": pl.Int64(),
            "previous_close_price": pl.Int64(),
            "price_change": pl.Float64(),
            "trade_count": pl.Int64(),
            "trade_volume": pl.Int64(),
            "trade_value": pl.Int64(),
        }
    )


def _order_book_schema() -> pl.Schema:
    return pl.Schema(
        {
            "tsetmc_instrument_code": pl.String(),
            "event_timestamp": pl.Datetime(time_zone="UTC"),
            "order_book_level": pl.Int64(),
            "bid_price": pl.Int64(),
            "bid_size": pl.Int64(),
            "bid_order_count": pl.Int64(),
            "ask_price": pl.Int64(),
            "ask_size": pl.Int64(),
            "ask_order_count": pl.Int64(),
        }
    )


def _investor_activity_schema() -> pl.Schema:
    return pl.Schema(
        {
            "tsetmc_instrument_code": pl.String(),
            "symbol": pl.String(),
            "event_timestamp": pl.Datetime(time_zone="UTC"),
            "individual_buy_count": pl.Int64(),
            "individual_buy_volume": pl.Int64(),
            "individual_buy_value": pl.Int64(),
            "individual_sell_count": pl.Int64(),
            "individual_sell_volume": pl.Int64(),
            "individual_sell_value": pl.Int64(),
            "institutional_buy_count": pl.Int64(),
            "institutional_buy_volume": pl.Int64(),
            "institutional_buy_value": pl.Int64(),
            "institutional_sell_count": pl.Int64(),
            "institutional_sell_volume": pl.Int64(),
            "institutional_sell_value": pl.Int64(),
        }
    )


def _empty_daily_prices() -> pl.DataFrame:
    return pl.DataFrame(schema=_daily_schema())


def _parse_yyyymmdd(value: int, field: str) -> date:
    return _parse_date_text(str(value), field)


def _optional_source_date(value: int | None, field: str) -> date | None:
    if value is None or value == 0:
        return None
    return _parse_yyyymmdd(value, field)


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


def _optional_event_timestamp(local_date: date | None, value: int | None) -> datetime | None:
    if local_date is None or value in {None, 0}:
        return None
    return _event_timestamp(local_date, value)


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
    if value is None:
        return None
    result = str(value).strip()
    return result or None


def _optional_integral(value: str | int | float | None, field: str) -> int | None:
    if value is None or (isinstance(value, str) and value.strip().lower() in {"", "-", "null"}):
        return None
    try:
        number = float(value)
    except ValueError as exc:
        raise SchemaValidationError(f"Source field {field!r} is not numeric.") from exc
    if not number.is_integer():
        raise SchemaValidationError(f"Source field {field!r} is not integral.")
    return int(number)


def _optional_bool_flag(value: int | None, field: str) -> bool | None:
    if value is None:
        return None
    if value not in {0, 1}:
        raise SchemaValidationError(f"Source field {field!r} is not a zero/one flag.")
    return bool(value)


def _optional_float(value: str | float | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, str) and value.strip().lower() in {"", "-", "—", "null"}:
        return None
    try:
        return float(value)
    except ValueError as exc:
        raise SchemaValidationError("price-to-earnings ratio is malformed.") from exc
