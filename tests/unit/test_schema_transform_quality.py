"""Schema drift and financial transform contracts."""

import json
from datetime import UTC, date, datetime

import polars as pl
import pytest

from oxtapus.data.quality import validate_daily_prices
from oxtapus.data.schema import schema_diff, schema_fingerprint
from oxtapus.domain.errors import ResponseValidationError, SchemaValidationError
from oxtapus.providers.tsetmc.parsers import parse_object, parse_records
from oxtapus.providers.tsetmc.queries import DailyPriceQuery, MarketWatchQuery
from oxtapus.providers.tsetmc.transformers import transform_daily_prices, transform_market_watch
from oxtapus.transport.base import RawResponse


def raw(body: object) -> RawResponse:
    return RawResponse(
        "request",
        "operation",
        "fixture",
        "test",
        "https://example.invalid",
        200,
        {"content-type": "application/json"},
        json.dumps(body).encode(),
        datetime.now(UTC),
        0.1,
        0,
    )


def test_schema_fingerprint_and_diff() -> None:
    first = {"a": 1, "nested": {"b": "x"}}
    second = {"a": "changed", "nested": {"b": "x"}, "c": True}
    assert schema_fingerprint(first) == schema_fingerprint(first)
    diff = schema_diff(first, second)
    assert "$.c" in diff.added_fields
    assert "$.a" in diff.changed_types
    assert diff.changed


def test_parsers_reject_malformed_json_and_wrong_envelopes() -> None:
    malformed = raw({"wrong": []})
    with pytest.raises(ResponseValidationError):
        parse_records(malformed, "expected")
    with pytest.raises(ResponseValidationError):
        parse_object(raw({"expected": []}), "expected")
    bad = raw({})
    object.__setattr__(bad, "content", b"{")
    with pytest.raises(ResponseValidationError):
        bad.json()


def test_daily_transform_preserves_nulls_and_filters_dates() -> None:
    output = transform_daily_prices(
        [
            {
                "insCode": "12345",
                "dEven": 20250102,
                "priceFirst": 10,
                "priceMax": 12,
                "priceMin": 9,
                "pClosing": 11,
                "pDrCotVal": None,
                "priceYesterday": 10,
                "zTotTran": 0,
                "qTotTran5J": 0,
                "qTotCap": 0,
                "additive": "reported",
            }
        ],
        DailyPriceQuery(
            tsetmc_instrument_code="12345",
            symbol="نماد",
            start=date(2025, 1, 1),
        ),
    )
    assert output.data.item(0, "last_price") is None
    assert output.data.schema["close_price"] == pl.Int64
    assert output.unknown_fields == ("additive",)


def test_daily_transform_rejects_changed_required_types() -> None:
    with pytest.raises(SchemaValidationError):
        transform_daily_prices(
            [{"insCode": "12345", "dEven": "bad"}],
            DailyPriceQuery(tsetmc_instrument_code="12345", symbol="نماد"),
        )


def test_market_timestamp_is_tehran_aware() -> None:
    output = transform_market_watch(
        [
            {
                "insCode": "12345",
                "insID": "IRO1TEST0001",
                "lva": "نماد",
                "lvc": "نام",
                "hEven": 123045,
            }
        ],
        MarketWatchQuery(instrument_types=("equity",)),
        datetime(2026, 8, 29, tzinfo=UTC),
    )
    timestamp = output.data.item(0, "event_timestamp")
    assert timestamp.utcoffset() is not None
    assert timestamp.hour == 12


def test_market_missing_ratio_sentinel_becomes_null_not_zero() -> None:
    output = transform_market_watch(
        [
            {
                "insCode": "12345",
                "insID": "IRO1TEST0001",
                "lva": "نماد",
                "lvc": "نام",
                "pe": "-",
            }
        ],
        MarketWatchQuery(instrument_types=("equity",)),
        datetime(2026, 8, 29, tzinfo=UTC),
    )
    assert output.data.item(0, "price_to_earnings_ratio") is None


def test_quality_reports_duplicates_and_invalid_prices() -> None:
    frame = pl.DataFrame(
        {
            "tsetmc_instrument_code": ["1", "1"],
            "trading_date": [date(2025, 1, 1)] * 2,
            "high_price": [9, 9],
            "low_price": [10, 10],
            "close_price": [-1, -1],
        }
    )
    report = validate_daily_prices(frame)
    assert not report.passed
    assert {issue.rule for issue in report.issues} >= {
        "primary_key_unique",
        "daily_high_not_below_low",
        "close_price_non_negative",
    }
