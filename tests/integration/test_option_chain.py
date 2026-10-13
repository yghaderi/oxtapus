"""Bulk option selection, sync/async parity, and replay contracts."""

import polars as pl
import pytest

import oxtapus as ox
from oxtapus.application.ingestion import IngestionPipeline
from oxtapus.domain.enums import DataLayer
from oxtapus.domain.errors import InvalidInstrumentIdentifierError
from oxtapus.progress.reporter import make_progress_reporter
from oxtapus.providers.tsetmc.provider import TsetmcProvider
from oxtapus.providers.tsetmc.queries import OptionChainQuery
from oxtapus.providers.tsetmc.transformers import transform_option_chain
from oxtapus.storage.memory import MemoryStorage

_SELECTIONS = [
    (None, {"فولاد", "خودرو"}),
    ("فولاد", {"فولاد"}),
    (["فولاد", "خودرو"], {"فولاد", "خودرو"}),
    (("  فولاد  ", "فولاد"), {"فولاد"}),
    ("65883838195688438", {"خودرو"}),
    (["فولاد", "46348559193224090"], {"فولاد"}),
    ("ناشناخته", set()),
]


def assert_bulk_result(frame: pl.DataFrame, expected: set[str], requests) -> None:
    assert set(frame["underlying_symbol"]) == expected
    assert frame.height == len(expected) * 2
    assert frame.schema["tsetmc_instrument_code"] == pl.String
    assert frame.schema["expiration_date"] == pl.Date
    assert frame.schema["last_price"] == pl.Int64
    assert frame["last_price"].null_count() == frame.height
    assert frame["tsetmc_instrument_code"].n_unique() == frame.height
    assert len(requests) == 1
    assert requests[0].url.endswith("/GetInstrumentOptionMarketWatch/0")


@pytest.mark.parametrize(("underlying", "expected"), _SELECTIONS)
def test_sync_option_chain_uses_one_bulk_request(underlying, expected, sync_transport) -> None:
    with ox.Client(transport=sync_transport) as client:
        result = client.market.fetch_option_chain(underlying)
    assert_bulk_result(result.data, expected, sync_transport.requests)
    assert result.endpoint == "option_market_watch"
    assert not result.failures


@pytest.mark.parametrize(("underlying", "expected"), _SELECTIONS)
async def test_async_option_chain_uses_one_bulk_request(
    underlying, expected, async_transport
) -> None:
    async with ox.AsyncClient(transport=async_transport) as client:
        frame = await client.market.option_chain(underlying)
    assert_bulk_result(frame, expected, async_transport.requests)


@pytest.mark.parametrize(
    ("underlying", "error"),
    [
        ([], ValueError),
        ("  ", InvalidInstrumentIdentifierError),
        ([""], InvalidInstrumentIdentifierError),
        ([1], TypeError),
        (1, TypeError),
    ],
)
def test_invalid_selection_fails_before_remote_access(underlying, error, sync_transport) -> None:
    with ox.Client(transport=sync_transport) as client, pytest.raises(error):
        client.market.option_chain(underlying)
    assert not sync_transport.requests


@pytest.mark.parametrize(
    ("underlying", "error"),
    [([], ValueError), ([""], InvalidInstrumentIdentifierError), ([1], TypeError)],
)
async def test_async_invalid_selection_fails_before_remote_access(
    underlying, error, async_transport
) -> None:
    async with ox.AsyncClient(transport=async_transport) as client:
        with pytest.raises(error):
            await client.market.option_chain(underlying)
    assert not async_transport.requests


def test_isin_selection_still_resolves_to_an_underlying_code(sync_transport) -> None:
    with ox.Client(transport=sync_transport) as client:
        frame = client.market.option_chain("IRO1FOLD0001")
    assert set(frame["underlying_symbol"]) == {"فولاد"}
    assert (
        sum("GetInstrumentOptionMarketWatch" in request.url for request in sync_transport.requests)
        == 1
    )


async def test_async_isin_selection_still_resolves_to_an_underlying_code(async_transport) -> None:
    async with ox.AsyncClient(transport=async_transport) as client:
        frame = await client.market.option_chain("IRO1FOLD0001")
    assert set(frame["underlying_symbol"]) == {"فولاد"}
    assert (
        sum("GetInstrumentOptionMarketWatch" in request.url for request in async_transport.requests)
        == 1
    )


def test_source_qualified_shortcut_defaults_to_all(monkeypatch, sync_transport) -> None:
    monkeypatch.setattr(ox.tsetmc, "Client", lambda: ox.Client(transport=sync_transport))
    frame = ox.tsetmc.option_chain()
    assert_bulk_result(frame, {"فولاد", "خودرو"}, sync_transport.requests)


def test_empty_option_snapshot_retains_canonical_schema() -> None:
    frame = transform_option_chain([], OptionChainQuery()).data
    assert frame.is_empty()
    assert frame.schema["strike_price"] == pl.Int64
    assert frame.schema["expiration_date"] == pl.Date


def test_filtered_option_replay_reads_the_saved_bulk_response(sync_transport) -> None:
    provider = TsetmcProvider(sync_transport)
    query = OptionChainQuery(underlyings=("خودرو",))
    execution = provider.option_chain(
        query, reporter=make_progress_reporter(False), operation_id="options"
    )
    storage = MemoryStorage()
    pipeline = IngestionPipeline(
        storage,
        provider.fetchers.options,
        silver_dataset="option_quote",
        gold_dataset="option_chain",
    )
    pipeline.ingest(execution)
    pipeline.replay(execution.response.request_id, query)
    frame = storage.read_frame("option_chain", DataLayer.GOLD)
    assert_bulk_result(frame, {"خودرو"}, sync_transport.requests)


@pytest.mark.parametrize("underlying", [None, ["فولاد", "خودرو"]])
def test_ingestion_accepts_all_or_multiple_underlyings(underlying, sync_transport) -> None:
    storage = MemoryStorage()
    with ox.Client(transport=sync_transport, storage=storage) as client:
        run = client.ingestion.option_chain(underlying)
    assert not run.failures
    frame = storage.read_frame("option_chain", DataLayer.GOLD)
    assert_bulk_result(frame, {"فولاد", "خودرو"}, sync_transport.requests)
