"""In-memory storage for notebooks and tests."""

from __future__ import annotations

import hashlib

import polars as pl

from oxtapus.data.catalog import DatasetSpec
from oxtapus.data.layers import BronzeRecord
from oxtapus.domain.enums import DataLayer
from oxtapus.storage.base import StorageWriteResult, WriteMode


class MemoryStorage:
    """Process-local idempotent storage with no configuration."""

    def __init__(self) -> None:
        self._frames: dict[tuple[DataLayer, str], pl.DataFrame] = {}
        self._bronze: dict[str, BronzeRecord] = {}

    def write_frame(
        self,
        dataset: str,
        layer: DataLayer,
        frame: pl.DataFrame,
        spec: DatasetSpec,
        *,
        mode: WriteMode = "merge",
    ) -> StorageWriteResult:
        """Store a frame, merging primary keys by default."""

        key = (layer, dataset)
        current = self._frames.get(key)
        combined = frame
        if current is not None and mode != "replace":
            combined = pl.concat([current, frame], how="diagonal_relaxed")
        if mode == "merge" and spec.primary_key:
            combined = combined.unique(
                subset=list(spec.primary_key), keep="last", maintain_order=True
            )
        self._frames[key] = combined
        checksum = hashlib.sha256(combined.write_json().encode()).hexdigest()
        return StorageWriteResult(
            dataset, frame.height, 1, checksum, (f"memory://{layer}/{dataset}",)
        )

    def read_frame(self, dataset: str, layer: DataLayer) -> pl.DataFrame:
        """Return a clone so callers cannot mutate storage state."""

        return self._frames.get((layer, dataset), pl.DataFrame()).clone()

    def write_bronze(self, record: BronzeRecord) -> StorageWriteResult:
        """Store one immutable Bronze record idempotently."""

        existing = self._bronze.get(record.request_id)
        if existing is not None and existing.payload_checksum != record.payload_checksum:
            raise ValueError("A Bronze request ID cannot be overwritten with different content.")
        self._bronze[record.request_id] = record
        return StorageWriteResult(
            dataset=f"bronze/{record.capability}",
            rows_written=1,
            partitions_written=1,
            checksum=record.payload_checksum,
            paths=(f"memory://bronze/{record.request_id}",),
        )

    def read_bronze(self, request_id: str) -> BronzeRecord:
        """Return one stored Bronze record."""

        return self._bronze[request_id]
