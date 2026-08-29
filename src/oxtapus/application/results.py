"""Application-layer result values independent of presentation concerns."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import polars as pl

from oxtapus.data.lineage import Lineage
from oxtapus.domain.enums import DataLayer, ProviderCapability
from oxtapus.providers.base import FetchFailure


@dataclass(frozen=True, slots=True)
class ServiceResult:
    """Canonical data plus source, quality, and lineage metadata."""

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
