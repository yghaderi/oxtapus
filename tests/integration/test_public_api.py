# ruff: noqa: RUF001
"""Offline public API integration tests."""

import polars as pl
import pytest

from oxtapus import AsyncClient, Client
from oxtapus.domain.enums import DataLayer
from oxtapus.domain.errors import PartialFetchWarning, UnsupportedCapabilityError
from oxtapus.storage.memory import MemoryStorage


def test_sync_client_end_to_end(sync_transport) -> None:
    with Client(transport=sync_transport) as client:
        prices = client.market.daily_prices(["فولاد"], start="۱۴۰۳/۱۰/۱۲", end="۱۴۰۴/۱۰/۱۰")
        snapshot = client.market.market_watch(["equity"])
        quote = client.market.quote("فولاد")
        order_book = client.market.market_depth("فولاد")
        activity = client.market.investor_activity("فولاد")
        chain = client.market.option_chain("فولاد")
        instruments = client.instruments.search("فولاد")
        info = client.instruments.info("فولاد")
        identity = client.instruments.identity("فولاد")
        board = client.governance.board_members("فولاد")
        dollar = client.assets.history("دلار")
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
    assert quote.item(0, "last_price") == 4270
    assert quote.height == 1
    assert order_book.height == 2
    assert order_book.item(0, "bid_price") == 4260
    assert activity.item(0, "individual_buy_volume") == 150000
    assert set(chain["option_type"]) == {"put", "call"}
    assert instruments.item(0, "symbol") == "فولاد"
    assert info.item(0, "estimated_earnings_per_share") == 530
    assert identity.item(0, "subsector_name") == "تولید آهن و فولاد"
    assert board.item(0, "member_name") == "شرکت سرمایه گذاری نمونه"
    assert dollar.item(0, "asset_code") == "usd_irr"
    assert dollar.item(1, "price_change") == -2000
    assert advanced.provider == "tsetmc"
    assert advanced.quality_summary["passed"] is True
    assert sync_transport.close_calls == 0


def test_public_api_rejects_an_invalid_jalali_date_before_remote_access(sync_transport) -> None:
    with (
        Client(transport=sync_transport) as client,
        pytest.raises(ValueError, match=r"Invalid start='۱۴۰۳/۱۳/۰۱'.*YYYY-MM-DD"),
    ):
        client.assets.history("دلار", start="۱۴۰۳/۱۳/۰۱")

    assert sync_transport.requests == []


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
        quote = await client.market.quote("فولاد")
        order_book = await client.market.market_depth("فولاد")
        activity = await client.market.investor_activity("فولاد")
        chain = await client.market.option_chain("فولاد")
        instruments = await client.instruments.search("فولاد")
        info = await client.instruments.info("فولاد")
        identity = await client.instruments.identity("فولاد")
        board = await client.governance.board_members("فولاد")
        coin = await client.assets.history("emami_gold_coin")
        assert not client.closed
    assert prices.height == snapshot.height == instruments.height == 1
    assert quote.height == activity.height == info.height == identity.height == board.height == 1
    assert coin.height == 2
    assert coin.item(0, "asset_code") == "emami_gold_coin"
    assert order_book.height == 2
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
