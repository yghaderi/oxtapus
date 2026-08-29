"""Native asynchronous public client and namespaces."""

from __future__ import annotations

import warnings
from collections.abc import Sequence
from datetime import date

import polars as pl

from oxtapus.api._shared import normalize_symbols, parse_date, require_unadjusted
from oxtapus.api.results import FetchResult
from oxtapus.api.settings import Settings
from oxtapus.application.services import AsyncInstrumentService, AsyncMarketDataService
from oxtapus.domain.enums import ProviderCapability
from oxtapus.domain.errors import PartialFailureError, PartialFetchWarning
from oxtapus.progress.reporter import ProgressOption, ProgressReporter, make_progress_reporter
from oxtapus.providers.tsetmc.provider import AsyncTsetmcProvider
from oxtapus.providers.tsetmc.resolver import AsyncInstrumentResolver
from oxtapus.transport.async_httpx2 import Httpx2AsyncTransport
from oxtapus.transport.base import AsyncTransport
from oxtapus.transport.retry import RetryPolicy


class AsyncMarketNamespace:
    """Asynchronous market-data methods with no event-loop ownership."""

    def __init__(self, service: AsyncMarketDataService, settings: Settings) -> None:
        self._service = service
        self._settings = settings

    async def daily_prices(
        self,
        symbols: Sequence[str],
        start: date | str | None = None,
        end: date | str | None = None,
        *,
        adjusted: bool = False,
        progress: ProgressOption = None,
    ) -> pl.DataFrame:
        """Return canonical daily OHLCV using native async I/O."""

        result = await self.fetch_daily_prices(
            symbols,
            start,
            end,
            adjusted=adjusted,
            progress=progress,
        )
        _surface_failures(result)
        return result.data

    async def fetch_daily_prices(
        self,
        symbols: Sequence[str],
        start: date | str | None = None,
        end: date | str | None = None,
        *,
        adjusted: bool = False,
        progress: ProgressOption = None,
    ) -> FetchResult:
        """Return daily data and complete operational metadata."""

        require_unadjusted(adjusted)
        result = await self._service.daily_prices(
            normalize_symbols(symbols),
            start=parse_date(start, "start"),
            end=parse_date(end, "end"),
            reporter=self._reporter(progress),
        )
        return FetchResult.from_service(result)

    async def market_watch(
        self,
        instrument_types: Sequence[str] = ("equity", "etf"),
        *,
        progress: ProgressOption = None,
    ) -> pl.DataFrame:
        """Return the canonical market snapshot."""

        return (await self.fetch_market_watch(instrument_types, progress=progress)).data

    async def fetch_market_watch(
        self,
        instrument_types: Sequence[str] = ("equity", "etf"),
        *,
        progress: ProgressOption = None,
    ) -> FetchResult:
        """Return a market snapshot with operational metadata."""

        result = await self._service.market_watch(
            tuple(instrument_types), reporter=self._reporter(progress)
        )
        return FetchResult.from_service(result)

    async def option_chain(
        self, underlying: str, *, progress: ProgressOption = None
    ) -> pl.DataFrame:
        """Return one canonical row per option contract."""

        return (await self.fetch_option_chain(underlying, progress=progress)).data

    async def fetch_option_chain(
        self, underlying: str, *, progress: ProgressOption = None
    ) -> FetchResult:
        """Return option contracts with operational metadata."""

        result = await self._service.option_chain(underlying, reporter=self._reporter(progress))
        return FetchResult.from_service(result)

    def _reporter(self, option: ProgressOption) -> ProgressReporter:
        return make_progress_reporter(self._settings.progress if option is None else option)


class AsyncInstrumentNamespace:
    """Asynchronous instrument discovery methods."""

    def __init__(self, service: AsyncInstrumentService, settings: Settings) -> None:
        self._service = service
        self._settings = settings

    async def search(self, term: str, *, progress: ProgressOption = None) -> pl.DataFrame:
        """Search canonical instruments asynchronously."""

        return (await self.fetch_search(term, progress=progress)).data

    async def fetch_search(self, term: str, *, progress: ProgressOption = None) -> FetchResult:
        """Search instruments and include source metadata."""

        reporter = make_progress_reporter(self._settings.progress if progress is None else progress)
        return FetchResult.from_service(await self._service.search(term, reporter))


class AsyncClient:
    """Long-lived native asynchronous Oxtapus client."""

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        transport: AsyncTransport | None = None,
    ) -> None:
        self.settings = settings or Settings()
        self._owns_transport = transport is None
        self._transport = transport or _transport(self.settings)
        provider = AsyncTsetmcProvider(self._transport)
        resolver = AsyncInstrumentResolver(provider)
        self.market = AsyncMarketNamespace(
            AsyncMarketDataService(
                provider,
                resolver,
                concurrency=self.settings.concurrency,
                failure_mode=self.settings.failure_mode,
            ),
            self.settings,
        )
        self.instruments = AsyncInstrumentNamespace(AsyncInstrumentService(provider), self.settings)
        self._provider = provider
        self._closed = False

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Close transport resources owned by this client."""

        if self._closed:
            return
        if self._owns_transport:
            await self._transport.aclose()
        self._closed = True

    @property
    def closed(self) -> bool:
        """Whether this client has been closed."""

        return self._closed

    def capabilities(self) -> tuple[ProviderCapability, ...]:
        """Return verified provider capabilities without remote access."""

        return self._provider.capabilities()


def _transport(settings: Settings) -> Httpx2AsyncTransport:
    return Httpx2AsyncTransport(
        connect_timeout=settings.connect_timeout,
        read_timeout=settings.read_timeout,
        write_timeout=settings.write_timeout,
        pool_timeout=settings.pool_timeout,
        max_connections=settings.max_connections,
        max_keepalive_connections=settings.max_keepalive_connections,
        http2=settings.http2,
        verify=settings.verify_tls,
        proxy=settings.proxy,
        user_agent=settings.user_agent,
        requests_per_second=settings.requests_per_second,
        retry_policy=RetryPolicy(
            max_attempts=settings.retry_max_attempts,
            base_delay_seconds=settings.retry_base_delay,
            max_delay_seconds=settings.retry_max_delay,
            max_total_delay_seconds=settings.retry_total_delay_budget,
        ),
    )


def _surface_failures(result: FetchResult) -> None:
    if not result.failures:
        return
    failed = ", ".join(item.item for item in result.failures)
    if result.data.is_empty():
        raise PartialFailureError(f"All requested items failed: {failed}")
    warnings.warn(
        f"Some requested items failed and are absent from the result: {failed}",
        PartialFetchWarning,
        stacklevel=3,
    )
