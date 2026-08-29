"""Storage protocols."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol, runtime_checkable

import polars as pl

from oxtapus.data.catalog import DatasetSpec
from oxtapus.data.layers import BronzeRecord
from oxtapus.domain.enums import DataLayer

WriteMode = Literal["append", "merge", "replace"]


@dataclass(frozen=True, slots=True)
class StorageWriteResult:
    """Outcome of an idempotent storage write."""

    dataset: str
    rows_written: int
    partitions_written: int
    checksum: str
    paths: tuple[str, ...]


@runtime_checkable
class StorageBackend(Protocol):
    """Persistence boundary used by ingestion services."""

    def write_frame(
        self,
        dataset: str,
        layer: DataLayer,
        frame: pl.DataFrame,
        spec: DatasetSpec,
        *,
        mode: WriteMode = "merge",
    ) -> StorageWriteResult:
        """Persist a canonical or curated frame atomically."""

        ...

    def read_frame(self, dataset: str, layer: DataLayer) -> pl.DataFrame:
        """Read a persisted frame."""

        ...

    def write_bronze(self, record: BronzeRecord) -> StorageWriteResult:
        """Append one immutable raw response."""

        ...

    def read_bronze(self, request_id: str) -> BronzeRecord:
        """Read one immutable raw response."""

        ...
