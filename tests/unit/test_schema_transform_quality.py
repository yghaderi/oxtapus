"""Schema drift and financial transform contracts."""

import json
from datetime import UTC, date, datetime

import polars as pl
import pytest

from oxtapus.data.quality import validate_asset_prices, validate_daily_prices
from oxtapus.data.schema import schema_diff, schema_fingerprint
from oxtapus.domain.errors import (
    ResponseValidationError,
    SchemaValidationError,
    UnsupportedAssetError,
)
from oxtapus.providers.tgju.queries import AssetPriceHistoryQuery
from oxtapus.providers.tgju.transformers import transform_asset_price_history
from oxtapus.providers.tsetmc.parsers import parse_nullable_records, parse_object, parse_records
from oxtapus.providers.tsetmc.queries import (
    BoardMembersQuery,
    DailyPriceQuery,
    InvestorActivityQuery,
    MarketWatchQuery,
    OrderBookQuery,
    QuoteQuery,
)
from oxtapus.providers.tsetmc.transformers import (
    transform_board_members,
    transform_daily_prices,
    transform_investor_activity,
    transform_market_watch,
    transform_order_book,
    transform_quote,
)
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


def test_nullable_records_accepts_only_a_present_null_envelope() -> None:
    assert parse_nullable_records(raw({"bestLimits": None}), "bestLimits") == []
    with pytest.raises(ResponseValidationError):
        parse_nullable_records(raw({}), "bestLimits")


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


def test_quote_and_order_book_remain_distinct_canonical_datasets() -> None:
    quote = transform_quote(
        {
            "instrumentState": {
                "cEtaval": "A ",
                "cEtavalTitle": "مجاز",
                "underSupervision": 0,
            },
            "dEven": 20260831,
            "hEven": 123045,
            "pClosing": 4250.0,
            "pDrCotVal": 4270.0,
            "qTotTran5J": 200000.0,
        },
        QuoteQuery(tsetmc_instrument_code="12345", symbol="نماد"),
    )
    book = transform_order_book(
        [
            {
                "number": 1,
                "qTitMeDem": 10000,
                "zOrdMeDem": 4,
                "pMeDem": 4260,
                "pMeOf": 4270,
                "zOrdMeOf": 3,
                "qTitMeOf": 12000,
            }
        ],
        OrderBookQuery(tsetmc_instrument_code="12345"),
        datetime(2026, 8, 31, tzinfo=UTC),
    )
    assert quote.data.item(0, "last_price") == 4270
    assert quote.data.schema["last_price"] == pl.Int64
    assert "order_book_level" not in quote.data.columns
    assert book.data.item(0, "bid_price") == 4260
    assert "last_price" not in book.data.columns


def test_order_book_rejects_duplicate_levels() -> None:
    record = {"number": 1}
    with pytest.raises(SchemaValidationError):
        transform_order_book(
            [record, record],
            OrderBookQuery(tsetmc_instrument_code="12345"),
            datetime(2026, 8, 31, tzinfo=UTC),
        )


def test_investor_activity_preserves_unreported_values_as_null() -> None:
    output = transform_investor_activity(
        {
            "buy_I_Volume": 100,
            "buy_N_Volume": 20,
            "buy_CountI": 10,
            "buy_CountN": 2,
            "sell_I_Volume": 80,
            "sell_N_Volume": 40,
            "sell_CountI": 8,
            "sell_CountN": 4,
        },
        InvestorActivityQuery(tsetmc_instrument_code="12345", symbol="نماد"),
        datetime(2026, 8, 31, tzinfo=UTC),
    )
    assert output.data.item(0, "individual_buy_value") is None
    assert output.data.item(0, "institutional_sell_volume") == 40
    assert output.warnings


def test_board_members_flattens_xml_and_reports_xml_drift() -> None:
    content = """<Root><AssemblyDate>1405/05/20</AssemblyDate>
    <NewDisclosureField>new</NewDisclosureField><BoardMembers><BoardMember>
    <MemberName>عضو نمونه</MemberName><NationalCode_RegisterNumber>0012345678</NationalCode_RegisterNumber>
    <Designation>رئیس هیئت مدیره</Designation></BoardMember></BoardMembers></Root>"""
    output = transform_board_members(
        [
            {
                "title": "معرفی اعضای هیئت مدیره",
                "sentDateTime_Gregorian": "2026-08-11T12:10:00",
                "publishDateTime_Gregorian": "2026-08-11T12:20:00",
                "publishDateTime_DEven": 20260811,
                "reportSubType": 19,
                "pageID": -1,
                "content": content,
            }
        ],
        BoardMembersQuery(tsetmc_instrument_code="12345", symbol="نماد"),
    )
    assert output.data.item(0, "member_name") == "عضو نمونه"
    assert output.data.item(0, "publication_date") == date(2026, 8, 11)
    assert output.unknown_fields == ("content.NewDisclosureField",)


def test_board_members_rejects_unsafe_xml_declarations() -> None:
    with pytest.raises(SchemaValidationError):
        transform_board_members(
            [
                {
                    "title": "هیئت مدیره",
                    "sentDateTime_Gregorian": "2026-08-11T12:10:00",
                    "publishDateTime_Gregorian": "2026-08-11T12:20:00",
                    "publishDateTime_DEven": 20260811,
                    "reportSubType": 19,
                    "pageID": -1,
                    "content": "<!DOCTYPE Root><Root />",
                }
            ],
            BoardMembersQuery(tsetmc_instrument_code="12345", symbol="نماد"),
        )


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


def test_tgju_asset_history_is_canonical_signed_and_sorted() -> None:
    output = transform_asset_price_history(
        {
            "data": [
                [
                    "\u06f1\u06f0\u06f1,\u06f0\u06f0\u06f0",
                    "\u06f9\u06f8,\u06f0\u06f0\u06f0",
                    "\u06f1\u06f0\u06f1,\u06f5\u06f0\u06f0",
                    "\u06f9\u06f9,\u06f0\u06f0\u06f0",
                    '<span class="low" dir="ltr">\u06f2,\u06f0\u06f0\u06f0</span>',
                    '<span class="low" dir="ltr">\u06f1.\u06f9\u06f8%</span>',
                    "2026/09/27",
                    "\u06f1\u06f4\u06f0\u06f5/\u06f0\u06f7/\u06f0\u06f5",
                    "additive",
                ],
                [
                    "100,000",
                    "99,000",
                    "102,000",
                    "101,000",
                    '<span class="high" dir="ltr">1,000</span>',
                    '<span class="high" dir="ltr">1.00%</span>',
                    "2026/09/26",
                    "1405/07/04",
                ],
            ],
            "newRootField": True,
        },
        AssetPriceHistoryQuery(asset="سکه امامی"),
    )
    assert output.data["trading_date"].to_list() == [date(2026, 9, 26), date(2026, 9, 27)]
    assert output.data.item(0, "asset_code") == "emami_gold_coin"
    assert output.data.item(1, "price_change") == -2000
    assert output.data.item(1, "price_change_percentage") == -1.98
    assert output.data.item(1, "jalali_date") == "1405-07-05"
    assert output.data.schema["close_price"] == pl.Int64
    assert output.unknown_fields == ("data[*][8]", "newRootField")


def test_tgju_asset_history_filters_dates_and_preserves_missing_change() -> None:
    output = transform_asset_price_history(
        {
            "data": [
                [
                    "100",
                    "90",
                    "110",
                    "100",
                    '<span class="" dir="ltr">-</span>',
                    '<span class="" dir="ltr">-</span>',
                    "2026/09/26",
                    "1405/07/04",
                ],
                ["200", "190", "210", "205", "5", "2.5%", "2026/09/27", "1405/07/05"],
            ]
        },
        AssetPriceHistoryQuery(
            asset="half_gold_coin",
            start=date(2026, 9, 26),
            end=date(2026, 9, 26),
        ),
    )
    assert output.data.height == 1
    assert output.data.item(0, "price_change") is None
    assert output.data.item(0, "price_change_percentage") is None


def test_tgju_asset_history_rejects_legacy_or_ambiguous_names() -> None:
    with pytest.raises(UnsupportedAssetError):
        AssetPriceHistoryQuery(asset="usd")
    with pytest.raises(UnsupportedAssetError):
        AssetPriceHistoryQuery(asset="half_coin")
    with pytest.raises(UnsupportedAssetError):
        AssetPriceHistoryQuery(asset="سکه")


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("  دلار  ", "usd_irr"),
        ("دلار   نیما", "nima_usd_irr"),
        ("دلار‌نیمایی", "nima_usd_irr"),
        (" یورو ", "eur_irr"),
        ("سکه   امامی", "emami_gold_coin"),
        ("سکه‌امامی", "emami_gold_coin"),
        ("نیم سکه", "half_gold_coin"),
        ("نیم‌سکه", "half_gold_coin"),
        ("نیم\u00a0  سکه", "half_gold_coin"),
    ],
)
def test_tgju_asset_names_ignore_persian_spacing_variants(source: str, expected: str) -> None:
    assert AssetPriceHistoryQuery(asset=source).asset == expected


def test_tgju_unknown_asset_error_echoes_input_and_supported_assets() -> None:
    with pytest.raises(UnsupportedAssetError) as raised:
        AssetPriceHistoryQuery(asset="طلای آب شده")
    message = str(raised.value)
    assert "طلای آب شده" in message
    assert "usd_irr (دلار آزاد)" in message
    assert "nima_usd_irr (دلار نیما)" in message
    assert "eur_irr (یورو)" in message
    assert "emami_gold_coin (سکه امامی)" in message
    assert "half_gold_coin (نیم سکه)" in message


def test_tgju_asset_history_rejects_short_source_rows() -> None:
    with pytest.raises(SchemaValidationError):
        transform_asset_price_history(
            {"data": [["100", "90"]]},
            AssetPriceHistoryQuery(asset="usd_irr"),
        )


def test_asset_price_quality_uses_asset_and_date_primary_key() -> None:
    frame = pl.DataFrame(
        {
            "asset_code": ["usd_irr", "usd_irr"],
            "trading_date": [date(2026, 9, 26), date(2026, 9, 26)],
            "high_price": [100, 100],
            "low_price": [90, 90],
            "close_price": [95, 95],
        }
    )
    report = validate_asset_prices(frame)
    assert not report.passed
    assert report.quarantined_rows == 2
    assert {issue.rule for issue in report.issues} == {"primary_key_unique"}
