"""Replayable Bronze, Silver, and Gold ingestion orchestration."""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Generic, TypeVar

import polars as pl

from oxtapus._version import __version__
from oxtapus.data.catalog import DataCatalog, DatasetSpec
from oxtapus.data.layers import BronzeRecord
from oxtapus.data.lineage import Lineage, LineageNode
from oxtapus.data.quality import QualityReport, split_daily_prices, validate_daily_prices
from oxtapus.data.schema import schema_fingerprint
from oxtapus.domain.enums import DataLayer
from oxtapus.domain.errors import DataQualityError
from oxtapus.providers.base import Fetcher, FetchExecution, QueryModel
from oxtapus.storage.base import StorageBackend, StorageWriteResult
from oxtapus.transport.base import RawResponse

Q = TypeVar("Q", bound=QueryModel)


@dataclass(frozen=True, slots=True)
class LayeredIngestionResult:
    """Persisted layer outcomes plus their reproducible lineage."""

    bronze: StorageWriteResult
    silver: StorageWriteResult
    gold: StorageWriteResult | None
    quarantine: StorageWriteResult | None
    lineage: Lineage
    quality: QualityReport


class IngestionPipeline(Generic[Q]):
    """Persist one fetch and rebuild downstream layers without network access."""

    def __init__(
        self,
        storage: StorageBackend,
        fetcher: Fetcher[Q],
        *,
        silver_dataset: str,
        gold_dataset: str | None = None,
        catalog: DataCatalog | None = None,
        quality_policy: str = "error",
    ) -> None:
        self._storage = storage
        self._fetcher = fetcher
        self._silver_dataset = silver_dataset
        self._gold_dataset = gold_dataset
        self._catalog = catalog or DataCatalog.load()
        if quality_policy not in {"error", "quarantine", "report"}:
            raise ValueError("quality_policy must be error, quarantine, or report.")
        self._quality_policy = quality_policy

    def ingest(self, execution: FetchExecution[Q]) -> LayeredIngestionResult:
        """Persist source evidence, canonical data, and optional curated data."""

        run_id = uuid.uuid4().hex
        bronze = _bronze_from_response(execution.response, run_id)
        bronze_write = self._storage.write_bronze(bronze)
        return self._persist_downstream(
            bronze,
            execution.output.data,
            run_id=run_id,
            bronze_write=bronze_write,
        )

    def replay(self, request_id: str, query: Q) -> LayeredIngestionResult:
        """Reconstruct Silver and Gold only from immutable Bronze bytes."""

        bronze = self._storage.read_bronze(request_id)
        if not bronze.verify_checksum():
            raise ValueError("Bronze checksum verification failed before replay.")
        response = RawResponse(
            request_id=bronze.request_id,
            operation_id=bronze.run_id,
            endpoint=bronze.endpoint,
            capability=bronze.capability,
            url="bronze://replay",
            status_code=bronze.response_status,
            headers=bronze.response_headers,
            content=bronze.payload,
            retrieved_at=bronze.retrieved_at,
            elapsed_seconds=0.0,
            retry_count=bronze.retry_count,
        )
        normalized = self._fetcher.transform_query(query)
        silver = self._fetcher.transform(response, normalized).data
        bronze_write = StorageWriteResult(
            dataset=f"bronze/{bronze.capability}",
            rows_written=0,
            partitions_written=0,
            checksum=bronze.payload_checksum,
            paths=(f"bronze://{bronze.request_id}",),
        )
        return self._persist_downstream(
            bronze,
            silver,
            run_id=uuid.uuid4().hex,
            bronze_write=bronze_write,
        )

    def _persist_downstream(
        self,
        bronze: BronzeRecord,
        silver: pl.DataFrame,
        *,
        run_id: str,
        bronze_write: StorageWriteResult,
    ) -> LayeredIngestionResult:
        quality = _quality(self._silver_dataset, silver)
        silver_spec = self._catalog.get(self._silver_dataset)
        quarantine_write: StorageWriteResult | None = None
        if not quality.passed and self._quality_policy == "error":
            raise DataQualityError(f"{quality.dataset} failed {len(quality.issues)} quality rules.")
        if self._silver_dataset == "daily_price" and self._quality_policy == "quarantine":
            split = split_daily_prices(silver)
            silver = split.accepted
            if split.quarantined.height:
                quarantine_write = self._storage.write_frame(
                    f"{self._silver_dataset}_quarantine",
                    DataLayer.SILVER,
                    _partition_columns(split.quarantined, silver_spec),
                    silver_spec,
                    mode="append",
                )
        persisted_silver = _partition_columns(silver, silver_spec)
        silver_write = self._storage.write_frame(
            self._silver_dataset,
            DataLayer.SILVER,
            persisted_silver,
            silver_spec,
            mode="merge",
        )
        nodes = [
            LineageNode(
                dataset=f"raw/{bronze.capability}/{bronze.request_id}",
                layer=DataLayer.BRONZE,
                schema_version=bronze.source_schema_fingerprint,
                operation="immutable_capture",
            ),
            LineageNode(
                dataset=self._silver_dataset,
                layer=DataLayer.SILVER,
                schema_version=silver_spec.schema_version,
                operation="validate_and_canonicalize",
                inputs=(bronze.payload_checksum,),
            ),
        ]
        gold_write: StorageWriteResult | None = None
        if self._gold_dataset is not None:
            gold_spec = self._catalog.get(self._gold_dataset)
            gold = build_gold(self._gold_dataset, silver, bronze.retrieved_at)
            gold = _partition_columns(gold, gold_spec)
            gold_write = self._storage.write_frame(
                self._gold_dataset,
                DataLayer.GOLD,
                gold,
                gold_spec,
                mode="merge",
            )
            nodes.append(
                LineageNode(
                    dataset=self._gold_dataset,
                    layer=DataLayer.GOLD,
                    schema_version=gold_spec.schema_version,
                    operation="deterministic_curate",
                    inputs=(silver_write.checksum,),
                )
            )
        return LayeredIngestionResult(
            bronze=bronze_write,
            silver=silver_write,
            gold=gold_write,
            quarantine=quarantine_write,
            lineage=Lineage(run_id, tuple(nodes)),
            quality=quality,
        )


def build_gold(dataset: str, silver: pl.DataFrame, retrieved_at: datetime) -> pl.DataFrame:
    """Build business-ready datasets using pure deterministic transformations."""

    if dataset == "market_snapshot":
        return silver.with_columns(pl.lit(retrieved_at.date()).alias("snapshot_date")).unique(
            subset=["tsetmc_instrument_code"], keep="last", maintain_order=True
        )
    if dataset == "option_chain":
        return silver.unique(
            subset=["tsetmc_instrument_code"], keep="last", maintain_order=True
        ).sort(["underlying_symbol", "expiration_date", "strike_price", "option_type"])
    raise ValueError(f"No Gold transformation is registered for {dataset!r}.")


def _quality(dataset: str, frame: pl.DataFrame) -> QualityReport:
    if dataset == "daily_price":
        return validate_daily_prices(frame)
    return QualityReport(dataset, frame.height, frame.height, 0)


def _partition_columns(frame: pl.DataFrame, spec: DatasetSpec) -> pl.DataFrame:
    result = frame
    if "trading_year" in spec.partition_columns and "trading_year" not in result.columns:
        result = result.with_columns(pl.col("trading_date").dt.year().alias("trading_year"))
    if "snapshot_date" in spec.partition_columns and "snapshot_date" not in result.columns:
        result = result.with_columns(pl.lit(datetime.now(UTC).date()).alias("snapshot_date"))
    return result


def _bronze_from_response(response: RawResponse, run_id: str) -> BronzeRecord:
    payload = response.content
    return BronzeRecord(
        provider="tsetmc",
        capability=response.capability,
        endpoint=response.endpoint,
        request_id=response.request_id,
        run_id=run_id,
        retrieved_at=response.retrieved_at,
        source_timezone="Asia/Tehran",
        package_version=__version__,
        endpoint_catalog_version="2026.08.29",
        latency_seconds=response.elapsed_seconds,
        retry_count=response.retry_count,
        response_status=response.status_code,
        response_headers=response.headers,
        content_type=response.headers.get("content-type"),
        content_encoding=response.headers.get("content-encoding"),
        content_length=len(payload),
        etag=response.headers.get("etag"),
        last_modified=response.headers.get("last-modified"),
        payload_checksum=hashlib.sha256(payload).hexdigest(),
        source_schema_fingerprint=schema_fingerprint(response.json()),
        parser_version="1.0.0",
        payload=payload,
    )
