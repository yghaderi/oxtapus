"""Atomic storage, idempotency, checkpoints, and three-layer replay tests."""

from datetime import date

import polars as pl
import pytest

from oxtapus.application.ingestion import IngestionPipeline
from oxtapus.data.catalog import DataCatalog
from oxtapus.data.checkpoints import CheckpointStore
from oxtapus.domain.enums import DataLayer
from oxtapus.progress.reporter import make_progress_reporter
from oxtapus.providers.tsetmc.provider import TsetmcProvider
from oxtapus.providers.tsetmc.queries import MarketWatchQuery
from oxtapus.storage.memory import MemoryStorage
from oxtapus.storage.parquet import LocalParquetStorage


def test_memory_storage_merges_primary_keys() -> None:
    storage = MemoryStorage()
    spec = DataCatalog.load().get("daily_price")
    first = _daily_frame(100)
    second = _daily_frame(200)
    storage.write_frame("daily_price", DataLayer.SILVER, first, spec)
    storage.write_frame("daily_price", DataLayer.SILVER, second, spec)
    stored = storage.read_frame("daily_price", DataLayer.SILVER)
    assert stored.height == 1
    assert stored.item(0, "close_price") == 200


def test_local_parquet_is_atomic_partitioned_and_idempotent(tmp_path) -> None:
    storage = LocalParquetStorage(tmp_path)
    spec = DataCatalog.load().get("daily_price")
    storage.write_frame("daily_price", DataLayer.SILVER, _daily_frame(100), spec)
    result = storage.write_frame("daily_price", DataLayer.SILVER, _daily_frame(200), spec)
    stored = storage.read_frame("daily_price", DataLayer.SILVER)
    assert stored.height == 1
    assert stored.item(0, "close_price") == 200
    assert result.partitions_written == 1
    assert list(tmp_path.rglob("*.tmp")) == []
    assert list(tmp_path.rglob("_manifest.json"))


def test_checkpoint_supports_resume(tmp_path) -> None:
    store = CheckpointStore(tmp_path)
    assert not store.completed("daily_price", "year=2025")
    checkpoint = store.save("daily_price", "year=2025", completed=True, checksum="checksum")
    assert checkpoint.completed
    assert store.completed("daily_price", "year=2025", "checksum")
    assert not store.completed("daily_price", "year=2025", "other")


def test_optional_duckdb_query(tmp_path) -> None:
    pytest.importorskip("duckdb")
    from oxtapus.storage.duckdb import DuckDBStorage

    storage = DuckDBStorage(tmp_path)
    try:
        assert storage.query("select 1 as value").item(0, "value") == 1
    finally:
        storage.close()


def test_bronze_to_silver_to_gold_replay_uses_no_network(sync_transport) -> None:
    provider = TsetmcProvider(sync_transport)
    execution = provider.market_watch(
        MarketWatchQuery(instrument_types=("equity",)),
        reporter=make_progress_reporter(False),
        operation_id="initial-fetch",
    )
    request_count = len(sync_transport.requests)
    storage = MemoryStorage()
    pipeline = IngestionPipeline(
        storage,
        provider.fetchers.watch,
        silver_dataset="market_watch",
        gold_dataset="market_snapshot",
    )
    first = pipeline.ingest(execution)
    replayed = pipeline.replay(execution.response.request_id, execution.query)
    assert len(sync_transport.requests) == request_count
    assert first.bronze.checksum == replayed.bronze.checksum
    assert replayed.silver.rows_written == 1
    assert replayed.gold is not None
    assert [node.layer for node in replayed.lineage.nodes] == [
        DataLayer.BRONZE,
        DataLayer.SILVER,
        DataLayer.GOLD,
    ]
    gold = storage.read_frame("market_snapshot", DataLayer.GOLD)
    assert gold.height == 1
    assert "snapshot_date" in gold.columns


def _daily_frame(close: int) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "tsetmc_instrument_code": ["123"],
            "trading_date": [date(2025, 1, 2)],
            "trading_year": [2025],
            "close_price": [close],
        }
    )
