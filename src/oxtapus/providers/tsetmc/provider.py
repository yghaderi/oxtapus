"""Capability-oriented TSETMC provider."""

from __future__ import annotations

from oxtapus.domain.enums import ProviderCapability
from oxtapus.progress.reporter import ProgressReporter
from oxtapus.providers.base import AsyncFetchContext, FetchContext, FetchExecution
from oxtapus.providers.tsetmc.capabilities import EndpointCatalog
from oxtapus.providers.tsetmc.fetchers import (
    BoardMembersFetcher,
    DailyPricesFetcher,
    InstrumentIdentityFetcher,
    InstrumentInfoFetcher,
    InstrumentSearchFetcher,
    InvestorActivityFetcher,
    MarketWatchFetcher,
    OptionChainFetcher,
    OrderBookFetcher,
    QuoteFetcher,
)
from oxtapus.providers.tsetmc.queries import (
    BoardMembersQuery,
    DailyPriceQuery,
    InstrumentIdentityQuery,
    InstrumentInfoQuery,
    InstrumentSearchQuery,
    InvestorActivityQuery,
    MarketWatchQuery,
    OptionChainQuery,
    OrderBookQuery,
    QuoteQuery,
)
from oxtapus.transport.base import AsyncTransport, SyncTransport

_PUBLIC_CAPABILITIES = (
    ProviderCapability.INSTRUMENT_SEARCH,
    ProviderCapability.INSTRUMENT_MASTER,
    ProviderCapability.DAILY_PRICES,
    ProviderCapability.MARKET_WATCH,
    ProviderCapability.QUOTE,
    ProviderCapability.ORDER_BOOK,
    ProviderCapability.INVESTOR_ACTIVITY,
    ProviderCapability.BOARD_MEMBERS,
    ProviderCapability.OPTION_CHAIN,
)


class _FetcherSet:
    def __init__(self, catalog: EndpointCatalog) -> None:
        self.search = InstrumentSearchFetcher(catalog.get("instrument_search"))
        self.info = InstrumentInfoFetcher(catalog.get("instrument_info"))
        self.identity = InstrumentIdentityFetcher(catalog.get("instrument_identity"))
        self.daily = DailyPricesFetcher(catalog.get("daily_prices"))
        self.watch = MarketWatchFetcher(catalog.get("market_watch"))
        self.quote = QuoteFetcher(catalog.get("closing_price_info"))
        self.order_book = OrderBookFetcher(catalog.get("best_limits"))
        self.investor_activity = InvestorActivityFetcher(catalog.get("client_type"))
        self.board_members = BoardMembersFetcher(catalog.get("board_members"))
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

    def identity(
        self, query: InstrumentIdentityQuery, *, reporter: ProgressReporter, operation_id: str
    ) -> FetchExecution[InstrumentIdentityQuery]:
        return self.fetchers.identity.execute(query, self._context(reporter, operation_id))

    def daily_prices(
        self, query: DailyPriceQuery, *, reporter: ProgressReporter, operation_id: str
    ) -> FetchExecution[DailyPriceQuery]:
        return self.fetchers.daily.execute(query, self._context(reporter, operation_id))

    def market_watch(
        self, query: MarketWatchQuery, *, reporter: ProgressReporter, operation_id: str
    ) -> FetchExecution[MarketWatchQuery]:
        return self.fetchers.watch.execute(query, self._context(reporter, operation_id))

    def quote(
        self, query: QuoteQuery, *, reporter: ProgressReporter, operation_id: str
    ) -> FetchExecution[QuoteQuery]:
        return self.fetchers.quote.execute(query, self._context(reporter, operation_id))

    def order_book(
        self, query: OrderBookQuery, *, reporter: ProgressReporter, operation_id: str
    ) -> FetchExecution[OrderBookQuery]:
        return self.fetchers.order_book.execute(query, self._context(reporter, operation_id))

    def investor_activity(
        self, query: InvestorActivityQuery, *, reporter: ProgressReporter, operation_id: str
    ) -> FetchExecution[InvestorActivityQuery]:
        return self.fetchers.investor_activity.execute(query, self._context(reporter, operation_id))

    def board_members(
        self, query: BoardMembersQuery, *, reporter: ProgressReporter, operation_id: str
    ) -> FetchExecution[BoardMembersQuery]:
        return self.fetchers.board_members.execute(query, self._context(reporter, operation_id))

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

    async def identity(
        self, query: InstrumentIdentityQuery, *, reporter: ProgressReporter, operation_id: str
    ) -> FetchExecution[InstrumentIdentityQuery]:
        return await self.fetchers.identity.execute_async(
            query, self._context(reporter, operation_id)
        )

    async def daily_prices(
        self, query: DailyPriceQuery, *, reporter: ProgressReporter, operation_id: str
    ) -> FetchExecution[DailyPriceQuery]:
        return await self.fetchers.daily.execute_async(query, self._context(reporter, operation_id))

    async def market_watch(
        self, query: MarketWatchQuery, *, reporter: ProgressReporter, operation_id: str
    ) -> FetchExecution[MarketWatchQuery]:
        return await self.fetchers.watch.execute_async(query, self._context(reporter, operation_id))

    async def quote(
        self, query: QuoteQuery, *, reporter: ProgressReporter, operation_id: str
    ) -> FetchExecution[QuoteQuery]:
        return await self.fetchers.quote.execute_async(query, self._context(reporter, operation_id))

    async def order_book(
        self, query: OrderBookQuery, *, reporter: ProgressReporter, operation_id: str
    ) -> FetchExecution[OrderBookQuery]:
        return await self.fetchers.order_book.execute_async(
            query, self._context(reporter, operation_id)
        )

    async def investor_activity(
        self, query: InvestorActivityQuery, *, reporter: ProgressReporter, operation_id: str
    ) -> FetchExecution[InvestorActivityQuery]:
        return await self.fetchers.investor_activity.execute_async(
            query, self._context(reporter, operation_id)
        )

    async def board_members(
        self, query: BoardMembersQuery, *, reporter: ProgressReporter, operation_id: str
    ) -> FetchExecution[BoardMembersQuery]:
        return await self.fetchers.board_members.execute_async(
            query, self._context(reporter, operation_id)
        )

    async def option_chain(
        self, query: OptionChainQuery, *, reporter: ProgressReporter, operation_id: str
    ) -> FetchExecution[OptionChainQuery]:
        return await self.fetchers.options.execute_async(
            query, self._context(reporter, operation_id)
        )

    def _context(self, reporter: ProgressReporter, operation_id: str) -> AsyncFetchContext:
        return AsyncFetchContext(self.name, self.transport, reporter, operation_id)
