# ruff: noqa: RUF001
"""Identity, configuration, and result contract tests."""

from datetime import UTC, date, datetime

import polars as pl
import pytest
from pydantic import ValidationError

import oxtapus as ox
from oxtapus.api._shared import parse_date
from oxtapus.api.results import FetchResult
from oxtapus.api.settings import Settings
from oxtapus.data.lineage import Lineage, LineageNode
from oxtapus.domain.enums import DataLayer, ProviderCapability
from oxtapus.domain.identifiers import IdentifierKind, classify_identifier, normalize_persian


def test_root_surface_is_small_and_versioned() -> None:
    assert ox.__version__ == "1.1.1"
    assert set(ox.__all__) == {
        "AsyncClient",
        "Client",
        "DataLayer",
        "FetchResult",
        "Settings",
        "__version__",
        "asset_history",
        "board_members",
        "daily_prices",
        "instrument_identity",
        "instrument_info",
        "instrument_search",
        "investor_activity",
        "market_depth",
        "market_watch",
        "option_chain",
        "quote",
    }


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("فولاد", "فولاد"),
        ("فولاد\u200c ", "فولاد"),
        ("فولاد\u00a0  مبارکه", "فولاد مبارکه"),
        ("ي ك", "ی ک"),
    ],
)
def test_persian_normalization(source: str, expected: str) -> None:
    assert normalize_persian(source) == expected


def test_identifier_classification() -> None:
    assert classify_identifier("فولاد") is IdentifierKind.SYMBOL
    assert classify_identifier("46348559193224090") is IdentifierKind.TSETMC_INSTRUMENT_CODE
    assert classify_identifier("IRO1FOLD0001") is IdentifierKind.ISIN
    assert classify_identifier("ABC12345678X") is IdentifierKind.PROVIDER_INSTRUMENT_ID


@pytest.mark.parametrize(
    "source",
    [
        "1403-10-12",
        "1403/10/12",
        "1403.10.12",
        "14031012",
        "۱۴۰۳/۱۰/۱۲",
        "١٤٠٣/١٠/١٢",
        "  ۱۴۰۳/۱۰/۱۲  ",
    ],
)
def test_parse_date_accepts_common_jalali_formats(source: str) -> None:
    assert parse_date(source, "start") == date(2025, 1, 1)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("2025-01-01", date(2025, 1, 1)),
        ("2025/1/1", date(2025, 1, 1)),
        ("2025.01.01", date(2025, 1, 1)),
        ("20250101", date(2025, 1, 1)),
        (date(2025, 1, 1), date(2025, 1, 1)),
        (None, None),
    ],
)
def test_parse_date_accepts_gregorian_dates_and_optional_bounds(
    source: date | str | None, expected: date | None
) -> None:
    assert parse_date(source, "end") == expected


@pytest.mark.parametrize(
    "source",
    [
        "1403-13-01",
        "1403/10-12",
        "1403-10",
        "1403101",
        "1700-01-01",
        "not-a-date",
    ],
)
def test_parse_date_rejects_invalid_or_ambiguous_values(source: str) -> None:
    with pytest.raises(ValueError) as captured:
        parse_date(source, "start")

    message = str(captured.value)
    assert f"start={source!r}" in message
    assert "YYYY-MM-DD" in message
    assert "Jalali" in message


def test_settings_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OXTAPUS_CONCURRENCY", "7")
    monkeypatch.setenv("OXTAPUS_PROGRESS", "true")
    settings = Settings()
    assert settings.concurrency == 7
    assert settings.progress is True


def test_settings_reject_untrusted_hosts_and_providers() -> None:
    with pytest.raises(ValidationError):
        Settings(base_urls=("https://example.invalid",))
    with pytest.raises(ValidationError):
        Settings(provider="unverified")


def test_fetch_result_conversions() -> None:
    frame = pl.DataFrame({"symbol": ["فولاد"], "close_price": [4250]})
    result = FetchResult(
        data=frame,
        capability=ProviderCapability.DAILY_PRICES,
        provider="tsetmc",
        endpoint="daily_prices",
        query={},
        retrieved_at=datetime.now(UTC),
        elapsed=0.1,
        retry_count=0,
        warnings=(),
        failures=(),
        source_schema_version="source",
        canonical_schema_version="1.0.0",
        data_layer=DataLayer.SILVER,
        lineage=Lineage(
            "run",
            (LineageNode("daily_price", DataLayer.SILVER, "1.0.0", "canonicalize"),),
        ),
        quality_summary={"passed": True},
    )
    assert result.to_polars().equals(frame)
    assert result.to_lazy().collect().equals(frame)
    assert result.to_records() == [{"symbol": "فولاد", "close_price": 4250}]


def test_optional_result_conversions_when_installed() -> None:
    pytest.importorskip("pyarrow")
    pytest.importorskip("pandas")
    frame = pl.DataFrame({"value": [1]})
    result = FetchResult(
        frame,
        ProviderCapability.DAILY_PRICES,
        "tsetmc",
        "daily_prices",
        {},
        datetime.now(UTC),
        0,
        0,
        (),
        (),
        "source",
        "1.0.0",
        DataLayer.SILVER,
        Lineage("run", ()),
        {"passed": True},
    )
    assert result.to_arrow().num_rows == 1
    assert result.to_pandas().iloc[0, 0] == 1
