"""Structured data-quality checks for canonical datasets."""

from __future__ import annotations

from dataclasses import dataclass

import polars as pl

from oxtapus.domain.enums import QualitySeverity


@dataclass(frozen=True, slots=True)
class QualityIssue:
    """Outcome of one failed quality rule."""

    rule: str
    severity: QualitySeverity
    failed_rows: int
    message: str


@dataclass(frozen=True, slots=True)
class QualityReport:
    """Quality summary attached to a fetch or persisted partition."""

    dataset: str
    checked_rows: int
    accepted_rows: int
    quarantined_rows: int
    issues: tuple[QualityIssue, ...] = ()

    @property
    def passed(self) -> bool:
        """Whether no error-level rule failed."""

        return not any(issue.severity is QualitySeverity.ERROR for issue in self.issues)

    def summary(self) -> dict[str, int | bool]:
        """Return stable summary metrics."""

        return {
            "checked_rows": self.checked_rows,
            "accepted_rows": self.accepted_rows,
            "quarantined_rows": self.quarantined_rows,
            "issue_count": len(self.issues),
            "passed": self.passed,
        }


@dataclass(frozen=True, slots=True)
class QualitySplit:
    """Accepted and quarantined rows produced by deterministic quality rules."""

    accepted: pl.DataFrame
    quarantined: pl.DataFrame
    report: QualityReport


def validate_daily_prices(frame: pl.DataFrame) -> QualityReport:
    """Validate non-destructive daily-price invariants."""

    issues: list[QualityIssue] = []
    row_count = frame.height
    keys = ["tsetmc_instrument_code", "trading_date"]
    if all(key in frame.columns for key in keys):
        duplicates = frame.group_by(keys).len().filter(pl.col("len") > 1).height
        if duplicates:
            issues.append(
                QualityIssue(
                    rule="primary_key_unique",
                    severity=QualitySeverity.ERROR,
                    failed_rows=duplicates,
                    message="Instrument/date primary keys must be unique.",
                )
            )
    for column in (
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "last_price",
        "previous_close_price",
        "trade_count",
        "trade_volume",
        "trade_value",
    ):
        if column in frame.columns:
            failed = frame.filter(pl.col(column).is_not_null() & (pl.col(column) < 0)).height
            if failed:
                issues.append(
                    QualityIssue(
                        rule=f"{column}_non_negative",
                        severity=QualitySeverity.ERROR,
                        failed_rows=failed,
                        message=f"{column} cannot be negative.",
                    )
                )
    if {"high_price", "low_price"} <= set(frame.columns):
        failed = frame.filter(
            pl.col("high_price").is_not_null()
            & pl.col("low_price").is_not_null()
            & (pl.col("high_price") < pl.col("low_price"))
        ).height
        if failed:
            issues.append(
                QualityIssue(
                    rule="daily_high_not_below_low",
                    severity=QualitySeverity.ERROR,
                    failed_rows=failed,
                    message="high_price must be greater than or equal to low_price.",
                )
            )
    _, quarantined = _split_daily_rows(frame)
    return QualityReport(
        dataset="fact_daily_price",
        checked_rows=row_count,
        accepted_rows=row_count - quarantined.height,
        quarantined_rows=quarantined.height,
        issues=tuple(issues),
    )


def validate_asset_prices(frame: pl.DataFrame) -> QualityReport:
    """Validate canonical non-security asset-price history."""

    issues = _price_issues(frame, keys=("asset_code", "trading_date"))
    invalid = _invalid_price_rows(frame, keys=("asset_code", "trading_date"))
    quarantined = frame.filter(invalid)
    return QualityReport(
        dataset="asset_price_history",
        checked_rows=frame.height,
        accepted_rows=frame.height - quarantined.height,
        quarantined_rows=quarantined.height,
        issues=tuple(issues),
    )


def split_daily_prices(frame: pl.DataFrame) -> QualitySplit:
    """Split invalid daily rows for an explicit quarantine policy."""

    accepted, quarantined = _split_daily_rows(frame)
    return QualitySplit(accepted, quarantined, validate_daily_prices(frame))


def _split_daily_rows(frame: pl.DataFrame) -> tuple[pl.DataFrame, pl.DataFrame]:
    invalid = _invalid_price_rows(
        frame,
        keys=("tsetmc_instrument_code", "trading_date"),
        extra_non_negative=(
            "last_price",
            "previous_close_price",
            "trade_count",
            "trade_volume",
            "trade_value",
        ),
    )
    return frame.filter(~invalid), frame.filter(invalid)


def _price_issues(
    frame: pl.DataFrame,
    *,
    keys: tuple[str, ...],
) -> list[QualityIssue]:
    issues: list[QualityIssue] = []
    if set(keys) <= set(frame.columns):
        duplicates = frame.group_by(list(keys)).len().filter(pl.col("len") > 1).height
        if duplicates:
            issues.append(
                QualityIssue(
                    rule="primary_key_unique",
                    severity=QualitySeverity.ERROR,
                    failed_rows=duplicates,
                    message="Asset/date primary keys must be unique.",
                )
            )
    for column in (
        "open_price",
        "high_price",
        "low_price",
        "close_price",
    ):
        if column in frame.columns:
            failed = frame.filter(pl.col(column).is_not_null() & (pl.col(column) < 0)).height
            if failed:
                issues.append(
                    QualityIssue(
                        rule=f"{column}_non_negative",
                        severity=QualitySeverity.ERROR,
                        failed_rows=failed,
                        message=f"{column} cannot be negative.",
                    )
                )
    if {"high_price", "low_price"} <= set(frame.columns):
        failed = frame.filter(
            pl.col("high_price").is_not_null()
            & pl.col("low_price").is_not_null()
            & (pl.col("high_price") < pl.col("low_price"))
        ).height
        if failed:
            issues.append(
                QualityIssue(
                    rule="daily_high_not_below_low",
                    severity=QualitySeverity.ERROR,
                    failed_rows=failed,
                    message="high_price must be greater than or equal to low_price.",
                )
            )
    return issues


def _invalid_price_rows(
    frame: pl.DataFrame,
    *,
    keys: tuple[str, ...],
    extra_non_negative: tuple[str, ...] = (),
) -> pl.Expr:
    invalid = pl.lit(False)
    if set(keys) <= set(frame.columns):
        invalid |= pl.struct(list(keys)).is_duplicated()
    for column in (
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        *extra_non_negative,
    ):
        if column in frame.columns:
            invalid |= pl.col(column).is_not_null() & (pl.col(column) < 0)
    if {"high_price", "low_price"} <= set(frame.columns):
        invalid |= (
            pl.col("high_price").is_not_null()
            & pl.col("low_price").is_not_null()
            & (pl.col("high_price") < pl.col("low_price"))
        )
    return invalid
