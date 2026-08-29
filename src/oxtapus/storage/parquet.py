"""Atomic local Parquet datasets with Hive-style partitions."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import polars as pl

from oxtapus.data.catalog import DatasetSpec
from oxtapus.data.layers import BronzeRecord
from oxtapus.domain.enums import DataLayer
from oxtapus.domain.errors import StorageError
from oxtapus.storage.base import StorageWriteResult, WriteMode


class LocalParquetStorage:
    """Local atomic Parquet storage requiring no database server."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root).expanduser().resolve()

    def write_frame(
        self,
        dataset: str,
        layer: DataLayer,
        frame: pl.DataFrame,
        spec: DatasetSpec,
        *,
        mode: WriteMode = "merge",
    ) -> StorageWriteResult:
        """Write partitions through temporary files followed by atomic rename."""

        dataset_root = self.root / layer.value / dataset
        dataset_root.mkdir(parents=True, exist_ok=True)
        groups = _partition_groups(frame, spec.partition_columns)
        written: list[Path] = []
        try:
            for values, partition_frame in groups:
                partition_root = dataset_root
                for column, value in zip(spec.partition_columns, values, strict=True):
                    partition_root /= f"{column}={_partition_value(value)}"
                partition_root.mkdir(parents=True, exist_ok=True)
                final_path = partition_root / "part-00000.parquet"
                output = partition_frame
                if final_path.exists() and mode != "replace":
                    current = pl.read_parquet(final_path)
                    output = pl.concat([current, partition_frame], how="diagonal_relaxed")
                if mode == "merge" and spec.primary_key:
                    output = output.unique(
                        subset=list(spec.primary_key), keep="last", maintain_order=True
                    )
                if spec.sort_columns and set(spec.sort_columns) <= set(output.columns):
                    output = output.sort(list(spec.sort_columns))
                temporary = partition_root / ".part-00000.parquet.tmp"
                output.write_parquet(temporary, compression="zstd", statistics=True)
                os.replace(temporary, final_path)
                written.append(final_path)
            checksum = _dataset_checksum(written)
            self._write_manifest(dataset_root, dataset, layer, spec, written, checksum)
        except Exception as exc:
            raise StorageError(f"Atomic Parquet write failed for {dataset!r}.") from exc
        return StorageWriteResult(
            dataset=dataset,
            rows_written=frame.height,
            partitions_written=len(written),
            checksum=checksum,
            paths=tuple(str(path) for path in written),
        )

    def read_frame(self, dataset: str, layer: DataLayer) -> pl.DataFrame:
        """Scan all committed Parquet partitions and collect them."""

        root = self.root / layer.value / dataset
        paths = sorted(root.rglob("*.parquet")) if root.exists() else []
        paths = [path for path in paths if not path.name.startswith(".")]
        if not paths:
            return pl.DataFrame()
        return pl.scan_parquet([str(path) for path in paths], hive_partitioning=False).collect()

    def scan_frame(self, dataset: str, layer: DataLayer) -> pl.LazyFrame:
        """Return a lazy scan when committed data exists."""

        root = self.root / layer.value / dataset
        return pl.scan_parquet(str(root / "**" / "*.parquet"), hive_partitioning=True)

    def write_bronze(self, record: BronzeRecord) -> StorageWriteResult:
        """Persist raw bytes and sanitized metadata as an append-only pair."""

        date = record.retrieved_at.date().isoformat()
        root = (
            self.root / DataLayer.BRONZE.value / "_raw" / record.provider / record.capability / date
        )
        root.mkdir(parents=True, exist_ok=True)
        payload_path = root / f"{record.request_id}.payload"
        metadata_path = root / f"{record.request_id}.metadata.json"
        if payload_path.exists():
            existing = hashlib.sha256(payload_path.read_bytes()).hexdigest()
            if existing != record.payload_checksum:
                raise StorageError("An immutable Bronze request ID already has different content.")
        else:
            payload_tmp = payload_path.with_suffix(".payload.tmp")
            payload_tmp.write_bytes(record.payload)
            os.replace(payload_tmp, payload_path)
        metadata = _json_safe(record.metadata())
        metadata_tmp = metadata_path.with_suffix(".json.tmp")
        metadata_tmp.write_text(json.dumps(metadata, sort_keys=True), encoding="utf-8")
        os.replace(metadata_tmp, metadata_path)
        return StorageWriteResult(
            dataset=f"bronze/{record.capability}",
            rows_written=1,
            partitions_written=1,
            checksum=record.payload_checksum,
            paths=(str(payload_path), str(metadata_path)),
        )

    def read_bronze(self, request_id: str) -> BronzeRecord:
        """Find and verify one persisted Bronze record."""

        matches = list(
            (self.root / DataLayer.BRONZE.value / "_raw").rglob(f"{request_id}.metadata.json")
        )
        if len(matches) != 1:
            raise StorageError(
                f"Expected one Bronze record for {request_id!r}; found {len(matches)}."
            )
        metadata_path = matches[0]
        payload_path = metadata_path.with_name(f"{request_id}.payload")
        values = json.loads(metadata_path.read_text(encoding="utf-8"))
        values["retrieved_at"] = datetime.fromisoformat(values["retrieved_at"])
        values["payload"] = payload_path.read_bytes()
        record = BronzeRecord(**values)
        if not record.verify_checksum():
            raise StorageError(f"Bronze checksum verification failed for {request_id!r}.")
        return record

    @staticmethod
    def _write_manifest(
        root: Path,
        dataset: str,
        layer: DataLayer,
        spec: DatasetSpec,
        paths: list[Path],
        checksum: str,
    ) -> None:
        manifest = {
            "dataset": dataset,
            "layer": layer.value,
            "schema_version": spec.schema_version,
            "primary_key": list(spec.primary_key),
            "partition_columns": list(spec.partition_columns),
            "files": [str(path.relative_to(root)) for path in paths],
            "checksum": checksum,
        }
        final_path = root / "_manifest.json"
        temporary = root / "._manifest.json.tmp"
        temporary.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
        os.replace(temporary, final_path)


def _partition_groups(
    frame: pl.DataFrame, columns: tuple[str, ...]
) -> list[tuple[tuple[Any, ...], pl.DataFrame]]:
    if not columns:
        return [((), frame)]
    missing = set(columns) - set(frame.columns)
    if missing:
        raise StorageError(f"Missing partition columns: {sorted(missing)}")
    result: list[tuple[tuple[Any, ...], pl.DataFrame]] = []
    for key, group in frame.partition_by(list(columns), as_dict=True, maintain_order=True).items():
        result.append((key, group))
    return result


def _partition_value(value: Any) -> str:
    return str(value).replace("/", "-").replace("\\", "-")


def _dataset_checksum(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.name.encode())
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def _json_safe(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value
