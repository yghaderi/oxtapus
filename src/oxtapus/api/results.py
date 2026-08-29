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
    """Canonical frame plus complete operational metadata."""

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
        """Construct the stable public view of an application result."""

        return cls(**{name: getattr(result, name) for name in cls.__dataclass_fields__})

    def to_polars(self) -> pl.DataFrame:
        """Return a cheap Polars clone."""

        return self.data.clone()

    def to_lazy(self) -> pl.LazyFrame:
        """Return a lazy plan over the in-memory result."""

        return self.data.lazy()

    def to_arrow(self) -> Any:
        """Convert to Arrow; requires the ``arrow`` extra."""

        try:
            return self.data.to_arrow()
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError("Install oxtapus[arrow] for Arrow conversion.") from exc

    def to_pandas(self) -> Any:
        """Convert to Pandas; requires the ``pandas`` and ``arrow`` extras."""

        try:
            return self.data.to_pandas()
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "Install oxtapus[pandas,arrow] for Pandas conversion."
            ) from exc

    def to_records(self) -> list[dict[str, Any]]:
        """Return Python dictionaries in row order."""

        return self.data.to_dicts()
