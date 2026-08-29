"""Offline public API integration tests."""

import polars as pl
import pytest

from oxtapus import AsyncClient, Client
from oxtapus.domain.enums import DataLayer
from oxtapus.domain.errors import PartialFetchWarning, UnsupportedCapabilityError
from oxtapus.storage.memory import MemoryStorage


def test_sync_client_end_to_end(sync_transport) -> None:
    with Client(transport=sync_transport) as client:
        prices = client.market.daily_prices(["فولاد"], start="2025-01-01", end="2025-12-31")
        snapshot = client.market.market_watch(["equity"])
        chain = client.market.option_chain("فولاد")
        instruments = client.instruments.search("فولاد")
        advanced = client.market.fetch_daily_prices(["فولاد"])
    assert isinstance(prices, pl.DataFrame)
    assert prices.columns[:4] == [
        "isin",
        "symbol",
        "tsetmc_instrument_code",
        "trading_date",
    ]
    assert prices.item(0, "last_price") is None
    assert snapshot.item(0, "symbol") == "فولاد"
    assert set(chain["option_type"]) == {"put", "call"}
    assert instruments.item(0, "symbol") == "فولاد"
    assert advanced.provider == "tsetmc"
    assert advanced.quality_summary["passed"] is True
    assert sync_transport.close_calls == 0


def test_sync_client_rejects_unverified_adjustments(sync_transport) -> None:
    with Client(transport=sync_transport) as client, pytest.raises(UnsupportedCapabilityError):
        client.market.daily_prices(["فولاد"], adjusted=True)


def test_client_owns_default_transport() -> None:
    client = Client()
    assert not client.closed
    client.close()
    assert client.closed
    client.close()


async def test_async_client_end_to_end(async_transport) -> None:
    async with AsyncClient(transport=async_transport) as client:
        prices = await client.market.daily_prices(["فولاد"])
        snapshot = await client.market.market_watch(["equity"])
        chain = await client.market.option_chain("فولاد")
        instruments = await client.instruments.search("فولاد")
        assert not client.closed
    assert prices.height == snapshot.height == instruments.height == 1
    assert chain.height == 2
    assert async_transport.close_calls == 0


async def test_async_client_owns_default_transport() -> None:
    client = AsyncClient()
    assert not client.closed
    await client.aclose()
    assert client.closed
    await client.aclose()


def test_partial_failure_is_reported(sync_transport) -> None:
    with Client(transport=sync_transport) as client:
        result = client.market.fetch_daily_prices(["فولاد", "ناشناخته"])
    assert result.data.height == 1
    assert len(result.failures) == 1
    assert result.failures[0].item == "ناشناخته"


def test_simple_batch_warns_about_partial_failure(sync_transport) -> None:
    with Client(transport=sync_transport) as client, pytest.warns(PartialFetchWarning):
        frame = client.market.daily_prices(["فولاد", "ناشناخته"])
    assert frame.height == 1


def test_configured_ingestion_namespace_persists_three_layers(sync_transport) -> None:
    storage = MemoryStorage()
    with Client(transport=sync_transport, storage=storage) as client:
        run = client.ingestion.market_watch(["equity"])
    assert len(run.results) == 1
    assert not run.failures
    assert storage.read_frame("market_watch", DataLayer.SILVER).height == 1
    assert storage.read_frame("market_snapshot", DataLayer.GOLD).height == 1
