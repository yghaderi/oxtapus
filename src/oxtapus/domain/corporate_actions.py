"""Canonical corporate-action schema contracts."""

from __future__ import annotations

import polars as pl

CORPORATE_ACTION_COLUMNS = (
    "isin",
    "corporate_action_type",
    "effective_date",
    "adjustment_factor",
    "shares_outstanding_before",
    "shares_outstanding_after",
)


def adjust_price_history(
    prices: pl.DataFrame,
    factors: pl.DataFrame,
    *,
    price_columns: tuple[str, ...] = (
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "last_price",
        "previous_close_price",
    ),
) -> pl.DataFrame:
    """Back-adjust earlier prices by later verified corporate-action factors.

    Each factor applies multiplicatively to rows strictly before its ``effective_date`` for
    the same ISIN. Missing price values remain null. The result adds ``adjusted_*`` Float64
    columns and ``cumulative_adjustment_factor``; it never overwrites official prices.
    """

    required_prices = {"isin", "trading_date"}
    required_factors = {"isin", "effective_date", "adjustment_factor"}
    if not required_prices <= set(prices.columns):
        raise ValueError(f"prices must contain {sorted(required_prices)}")
    if not required_factors <= set(factors.columns):
        raise ValueError(f"factors must contain {sorted(required_factors)}")
    factor_rows = factors.select(required_factors).to_dicts()
    expression = pl.lit(1.0)
    for item in factor_rows:
        factor = item["adjustment_factor"]
        if factor is None or float(factor) <= 0:
            raise ValueError("adjustment_factor must be positive and non-null.")
        expression *= (
            pl.when(
                (pl.col("isin") == item["isin"]) & (pl.col("trading_date") < item["effective_date"])
            )
            .then(float(factor))
            .otherwise(1.0)
        )
    result = prices.with_columns(expression.alias("cumulative_adjustment_factor"))
    available = [column for column in price_columns if column in result.columns]
    return result.with_columns(
        (pl.col(column).cast(pl.Float64) * pl.col("cumulative_adjustment_factor")).alias(
            f"adjusted_{column}"
        )
        for column in available
    )
