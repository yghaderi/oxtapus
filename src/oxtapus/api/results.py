# ruff: noqa: RUF002
"""Advanced public fetch result and explicit tabular conversions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import polars as pl

from oxtapus.application.results import ServiceResult
from oxtapus.data.lineage import Lineage
from oxtapus.domain.enums import DataLayer, ProviderCapability
from oxtapus.providers.base import FetchFailure


@dataclass(frozen=True, slots=True)
class FetchResult:
    """دیتافریم استاندارد همراه فرادادهٔ دریافت، گزارش کیفیت و lineage."""

    data: pl.DataFrame
    capability: ProviderCapability
    provider: str
    endpoint: str
    query: dict[str, Any]
    retrieved_at: datetime
    elapsed: float
    retry_count: int
    warnings: tuple[str, ...]
    failures: tuple[FetchFailure, ...]
    source_schema_version: str
    canonical_schema_version: str
    data_layer: DataLayer
    lineage: Lineage
    quality_summary: dict[str, int | bool]

    @classmethod
    def from_service(cls, result: ServiceResult) -> FetchResult:
        """یک نتیجهٔ application service را به قرارداد عمومی پایدار تبدیل می‌کند."""

        return cls(**{name: getattr(result, name) for name in cls.__dataclass_fields__})

    def to_polars(self) -> pl.DataFrame:
        """یک نسخهٔ کم‌هزینه از دیتافریم Polars برمی‌گرداند."""

        return self.data.clone()

    def to_lazy(self) -> pl.LazyFrame:
        """یک ``LazyFrame`` روی نتیجهٔ موجود در حافظه برمی‌گرداند."""

        return self.data.lazy()

    def to_arrow(self) -> Any:
        """نتیجه را به Arrow تبدیل می‌کند؛ extra با نام ``arrow`` لازم است."""

        try:
            return self.data.to_arrow()
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError("Install oxtapus[arrow] for Arrow conversion.") from exc

    def to_pandas(self) -> Any:
        """نتیجه را به Pandas تبدیل می‌کند؛ extraهای ``pandas`` و ``arrow`` لازم‌اند."""

        try:
            return self.data.to_pandas()
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "Install oxtapus[pandas,arrow] for Pandas conversion."
            ) from exc

    def to_records(self) -> list[dict[str, Any]]:
        """ردیف‌ها را به‌ترتیب به‌شکل فهرستی از دیکشنری‌های پایتون برمی‌گرداند."""

        return self.data.to_dicts()
