"""Capability-oriented TGJU provider."""

from __future__ import annotations

from oxtapus.domain.enums import ProviderCapability
from oxtapus.progress.reporter import ProgressReporter
from oxtapus.providers.base import AsyncFetchContext, FetchContext, FetchExecution
from oxtapus.providers.tgju.catalog import TgjuEndpointCatalog
from oxtapus.providers.tgju.fetcher import AssetPriceHistoryFetcher
from oxtapus.providers.tgju.queries import AssetPriceHistoryQuery
from oxtapus.transport.base import AsyncTransport, SyncTransport


class TgjuProvider:
    """Synchronous TGJU provider for agreement-covered verified assets."""

    name = "tgju"

    def __init__(
        self, transport: SyncTransport, catalog: TgjuEndpointCatalog | None = None
    ) -> None:
        self.transport = transport
        self.catalog = catalog or TgjuEndpointCatalog.load()
        self.history_fetcher = AssetPriceHistoryFetcher(self.catalog.get("asset_price_history"))

    def capabilities(self) -> tuple[ProviderCapability, ...]:
        """Return verified provider capabilities without network access."""

        return (ProviderCapability.ASSET_PRICE_HISTORY,)

    def asset_price_history(
        self,
        query: AssetPriceHistoryQuery,
        *,
        reporter: ProgressReporter,
        operation_id: str,
    ) -> FetchExecution[AssetPriceHistoryQuery]:
        """Fetch one supported asset history."""

        return self.history_fetcher.execute(
            query, FetchContext(self.name, self.transport, reporter, operation_id)
        )


class AsyncTgjuProvider:
    """Native asynchronous TGJU provider with feature parity."""

    name = "tgju"

    def __init__(
        self, transport: AsyncTransport, catalog: TgjuEndpointCatalog | None = None
    ) -> None:
        self.transport = transport
        self.catalog = catalog or TgjuEndpointCatalog.load()
        self.history_fetcher = AssetPriceHistoryFetcher(self.catalog.get("asset_price_history"))

    def capabilities(self) -> tuple[ProviderCapability, ...]:
        """Return verified provider capabilities without network access."""

        return (ProviderCapability.ASSET_PRICE_HISTORY,)

    async def asset_price_history(
        self,
        query: AssetPriceHistoryQuery,
        *,
        reporter: ProgressReporter,
        operation_id: str,
    ) -> FetchExecution[AssetPriceHistoryQuery]:
        """Fetch one supported asset history asynchronously."""

        return await self.history_fetcher.execute_async(
            query, AsyncFetchContext(self.name, self.transport, reporter, operation_id)
        )
