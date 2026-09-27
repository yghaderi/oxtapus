"""Conservative opt-in live source canary."""

import pytest

from oxtapus import Client, Settings


@pytest.mark.live
def test_official_instrument_search_canary() -> None:
    with Client(Settings(requests_per_second=1, retry_max_attempts=2)) as client:
        result = client.instruments.fetch_search("فولاد")
    assert result.data.height > 0
    assert "tsetmc_instrument_code" in result.data.columns
    assert result.source_schema_version


@pytest.mark.live
def test_official_quote_and_order_book_canary() -> None:
    with Client(Settings(requests_per_second=1, retry_max_attempts=2)) as client:
        quote = client.market.fetch_quote("778253364357513")
        order_book = client.market.fetch_market_depth("778253364357513")
    assert quote.data.height == 1
    assert quote.data.item(0, "tsetmc_instrument_code") == "778253364357513"
    assert order_book.data.height <= 5
    assert set(order_book.data.columns) >= {"bid_price", "ask_price", "order_book_level"}


@pytest.mark.live
@pytest.mark.parametrize(
    "asset",
    ["usd_irr", "nima_usd_irr", "eur_irr", "emami_gold_coin", "half_gold_coin"],
)
def test_tgju_asset_history_canary(asset: str) -> None:
    with Client(Settings(requests_per_second=1, retry_max_attempts=2)) as client:
        result = client.assets.fetch_history(asset)
    assert result.data.height > 0
    assert result.data.item(0, "asset_code") == asset
    assert result.data.schema["close_price"].is_integer()
