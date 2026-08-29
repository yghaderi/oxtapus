"""Pure calendar and corporate-action formula tests."""

from datetime import date

import polars as pl
import pytest

from oxtapus.data.quality import split_daily_prices
from oxtapus.domain.calendar import gregorian_to_jalali
from oxtapus.domain.corporate_actions import adjust_price_history


def test_jalali_convenience_conversion() -> None:
    assert gregorian_to_jalali(date(2025, 3, 21)) == (1404, 1, 1)


def test_adjusted_price_formula_preserves_official_prices_and_nulls() -> None:
    prices = pl.DataFrame(
        {
            "isin": ["IRTEST", "IRTEST"],
            "trading_date": [date(2025, 1, 1), date(2025, 1, 3)],
            "close_price": [100, 120],
            "last_price": [None, 121],
        }
    )
    factors = pl.DataFrame(
        {
            "isin": ["IRTEST"],
            "effective_date": [date(2025, 1, 2)],
            "adjustment_factor": [0.5],
        }
    )
    adjusted = adjust_price_history(prices, factors)
    assert adjusted["close_price"].to_list() == [100, 120]
    assert adjusted["adjusted_close_price"].to_list() == [50.0, 120.0]
    assert adjusted.item(0, "adjusted_last_price") is None


def test_adjustment_rejects_non_positive_factor() -> None:
    prices = pl.DataFrame({"isin": ["IRTEST"], "trading_date": [date(2025, 1, 1)]})
    factors = pl.DataFrame(
        {
            "isin": ["IRTEST"],
            "effective_date": [date(2025, 1, 2)],
            "adjustment_factor": [0.0],
        }
    )
    with pytest.raises(ValueError):
        adjust_price_history(prices, factors)


def test_invalid_daily_rows_are_split_for_quarantine() -> None:
    frame = pl.DataFrame(
        {
            "tsetmc_instrument_code": ["1", "2"],
            "trading_date": [date(2025, 1, 1), date(2025, 1, 1)],
            "high_price": [10, 8],
            "low_price": [9, 9],
            "close_price": [10, -1],
        }
    )
    split = split_daily_prices(frame)
    assert split.accepted.height == 1
    assert split.quarantined.height == 1
    assert split.report.quarantined_rows == 1
