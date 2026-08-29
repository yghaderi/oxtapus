"""Optional DuckDB query facade over local Parquet datasets."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

import polars as pl

from oxtapus.data.catalog import DatasetSpec
from oxtapus.data.layers import BronzeRecord
from oxtapus.domain.enums import DataLayer
from oxtapus.domain.errors import ConfigurationError
from oxtapus.storage.base import StorageWriteResult, WriteMode
from oxtapus.storage.parquet import LocalParquetStorage


class DuckDBStorage:
    """Parquet persistence plus optional DuckDB SQL query access."""

    def __init__(self, root: Path | str, database: Path | str = ":memory:") -> None:
        try:
            duckdb = importlib.import_module("duckdb")
        except ImportError as exc:
            raise ConfigurationError(
                "DuckDB storage requires the 'duckdb' optional dependency."
            ) from exc
        self._duckdb: Any = duckdb
        self._connection: Any = duckdb.connect(str(database))
        self._parquet = LocalParquetStorage(root)

    def write_frame(
        self,
        dataset: str,
        layer: DataLayer,
        frame: pl.DataFrame,
        spec: DatasetSpec,
        *,
        mode: WriteMode = "merge",
    ) -> StorageWriteResult:
        """Persist through the atomic Parquet backend."""

        return self._parquet.write_frame(dataset, layer, frame, spec, mode=mode)

    def read_frame(self, dataset: str, layer: DataLayer) -> pl.DataFrame:
        """Read through the Parquet backend."""

        return self._parquet.read_frame(dataset, layer)

    def write_bronze(self, record: BronzeRecord) -> StorageWriteResult:
        """Persist through the atomic Parquet backend."""

        return self._parquet.write_bronze(record)

    def read_bronze(self, request_id: str) -> BronzeRecord:
        """Read through the atomic Parquet backend."""

        return self._parquet.read_bronze(request_id)

    def query(self, sql: str) -> pl.DataFrame:
        """Execute SQL and return Polars without making network requests."""

        return self._connection.sql(sql).pl()

    def close(self) -> None:
        """Close the embedded database connection."""

        self._connection.close()
