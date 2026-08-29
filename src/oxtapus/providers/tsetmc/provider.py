"""Capability-oriented TSETMC provider."""

from __future__ import annotations

from oxtapus.domain.enums import ProviderCapability
from oxtapus.progress.reporter import ProgressReporter
from oxtapus.providers.base import AsyncFetchContext, FetchContext, FetchExecution
from oxtapus.providers.tsetmc.capabilities import EndpointCatalog
from oxtapus.providers.tsetmc.fetchers import (
    DailyPricesFetcher,
    InstrumentInfoFetcher,
    InstrumentSearchFetcher,
    MarketWatchFetcher,
    OptionChainFetcher,
)
from oxtapus.providers.tsetmc.queries import (
    DailyPriceQuery,
    InstrumentInfoQuery,
    InstrumentSearchQuery,
    MarketWatchQuery,
    OptionChainQuery,
)
from oxtapus.transport.base import AsyncTransport, SyncTransport

_PUBLIC_CAPABILITIES = (
    ProviderCapability.INSTRUMENT_SEARCH,
    ProviderCapability.INSTRUMENT_MASTER,
    ProviderCapability.DAILY_PRICES,
    ProviderCapability.MARKET_WATCH,
    ProviderCapability.OPTION_CHAIN,
)


class _FetcherSet:
    def __init__(self, catalog: EndpointCatalog) -> None:
        self.search = InstrumentSearchFetcher(catalog.get("instrument_search"))
        self.info = InstrumentInfoFetcher(catalog.get("instrument_info"))
        self.daily = DailyPricesFetcher(catalog.get("daily_prices"))
        self.watch = MarketWatchFetcher(catalog.get("market_watch"))
        self.options = OptionChainFetcher(catalog.get("option_market_watch"))


class TsetmcProvider:
    """Synchronous TSETMC provider using only verified endpoints."""

    name = "tsetmc"

    def __init__(self, transport: SyncTransport, catalog: EndpointCatalog | None = None) -> None:
        self.transport = transport
        self.catalog = catalog or EndpointCatalog.load()
        self.fetchers = _FetcherSet(self.catalog)

    def capabilities(self) -> tuple[ProviderCapability, ...]:
        """Return verified capabilities enabled by this implementation."""

        return _PUBLIC_CAPABILITIES

    def search(
        self, query: InstrumentSearchQuery, *, reporter: ProgressReporter, operation_id: str
    ) -> FetchExecution[InstrumentSearchQuery]:
        return self.fetchers.search.execute(query, self._context(reporter, operation_id))

    def info(
        self, query: InstrumentInfoQuery, *, reporter: ProgressReporter, operation_id: str
    ) -> FetchExecution[InstrumentInfoQuery]:
        return self.fetchers.info.execute(query, self._context(reporter, operation_id))

    def daily_prices(
        self, query: DailyPriceQuery, *, reporter: ProgressReporter, operation_id: str
    ) -> FetchExecution[DailyPriceQuery]:
        return self.fetchers.daily.execute(query, self._context(reporter, operation_id))

    def market_watch(
        self, query: MarketWatchQuery, *, reporter: ProgressReporter, operation_id: str
    ) -> FetchExecution[MarketWatchQuery]:
        return self.fetchers.watch.execute(query, self._context(reporter, operation_id))

    def option_chain(
        self, query: OptionChainQuery, *, reporter: ProgressReporter, operation_id: str
    ) -> FetchExecution[OptionChainQuery]:
        return self.fetchers.options.execute(query, self._context(reporter, operation_id))

    def _context(self, reporter: ProgressReporter, operation_id: str) -> FetchContext:
        return FetchContext(self.name, self.transport, reporter, operation_id)


class AsyncTsetmcProvider:
    """Asynchronous TSETMC provider with feature parity."""

    name = "tsetmc"

    def __init__(self, transport: AsyncTransport, catalog: EndpointCatalog | None = None) -> None:
        self.transport = transport
        self.catalog = catalog or EndpointCatalog.load()
        self.fetchers = _FetcherSet(self.catalog)

    def capabilities(self) -> tuple[ProviderCapability, ...]:
        """Return verified capabilities enabled by this implementation."""

        return _PUBLIC_CAPABILITIES

    async def search(
        self, query: InstrumentSearchQuery, *, reporter: ProgressReporter, operation_id: str
    ) -> FetchExecution[InstrumentSearchQuery]:
        return await self.fetchers.search.execute_async(
            query, self._context(reporter, operation_id)
        )

    async def info(
        self, query: InstrumentInfoQuery, *, reporter: ProgressReporter, operation_id: str
    ) -> FetchExecution[InstrumentInfoQuery]:
        return await self.fetchers.info.execute_async(query, self._context(reporter, operation_id))

    async def daily_prices(
        self, query: DailyPriceQuery, *, reporter: ProgressReporter, operation_id: str
    ) -> FetchExecution[DailyPriceQuery]:
        return await self.fetchers.daily.execute_async(query, self._context(reporter, operation_id))

    async def market_watch(
        self, query: MarketWatchQuery, *, reporter: ProgressReporter, operation_id: str
    ) -> FetchExecution[MarketWatchQuery]:
        return await self.fetchers.watch.execute_async(query, self._context(reporter, operation_id))

    async def option_chain(
        self, query: OptionChainQuery, *, reporter: ProgressReporter, operation_id: str
    ) -> FetchExecution[OptionChainQuery]:
        return await self.fetchers.options.execute_async(
            query, self._context(reporter, operation_id)
        )

    def _context(self, reporter: ProgressReporter, operation_id: str) -> AsyncFetchContext:
        return AsyncFetchContext(self.name, self.transport, reporter, operation_id)
