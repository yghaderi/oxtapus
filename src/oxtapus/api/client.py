"""Synchronous public client and capability namespaces."""

from __future__ import annotations

import warnings
from collections.abc import Sequence
from datetime import date

import polars as pl

from oxtapus.api._shared import normalize_symbols, parse_date, require_unadjusted
from oxtapus.api.results import FetchResult
from oxtapus.api.settings import Settings
from oxtapus.application.services import (
    IngestionRun,
    IngestionService,
    InstrumentService,
    MarketDataService,
)
from oxtapus.domain.enums import ProviderCapability
from oxtapus.domain.errors import PartialFailureError, PartialFetchWarning
from oxtapus.progress.reporter import ProgressOption, make_progress_reporter
from oxtapus.providers.tsetmc.provider import TsetmcProvider
from oxtapus.providers.tsetmc.resolver import InstrumentResolver
from oxtapus.storage.base import StorageBackend
from oxtapus.storage.duckdb import DuckDBStorage
from oxtapus.storage.memory import MemoryStorage
from oxtapus.storage.parquet import LocalParquetStorage
from oxtapus.transport.base import SyncTransport
from oxtapus.transport.retry import RetryPolicy
from oxtapus.transport.sync_httpx2 import Httpx2SyncTransport


class MarketNamespace:
    """Synchronous market-data methods."""

    def __init__(self, service: MarketDataService, settings: Settings) -> None:
        self._service = service
        self._settings = settings

    def daily_prices(
        self,
        symbols: Sequence[str],
        start: date | str | None = None,
        end: date | str | None = None,
        *,
        adjusted: bool = False,
        progress: ProgressOption = None,
    ) -> pl.DataFrame:
        """Return canonical daily OHLCV for resolved symbols or identifiers."""

        result = self.fetch_daily_prices(
            symbols,
            start,
            end,
            adjusted=adjusted,
            progress=progress,
        )
        _surface_failures(result)
        return result.data

    def fetch_daily_prices(
        self,
        symbols: Sequence[str],
        start: date | str | None = None,
        end: date | str | None = None,
        *,
        adjusted: bool = False,
        progress: ProgressOption = None,
    ) -> FetchResult:
        """Return daily data with source, retry, failure, quality, and lineage metadata."""

        require_unadjusted(adjusted)
        result = self._service.daily_prices(
            normalize_symbols(symbols),
            start=parse_date(start, "start"),
            end=parse_date(end, "end"),
            reporter=self._reporter(progress),
        )
        return FetchResult.from_service(result)

    def market_watch(
        self,
        instrument_types: Sequence[str] = ("equity", "etf"),
        *,
        progress: ProgressOption = None,
    ) -> pl.DataFrame:
        """Return the canonical latest bulk market snapshot."""

        return self.fetch_market_watch(instrument_types, progress=progress).data

    def fetch_market_watch(
        self,
        instrument_types: Sequence[str] = ("equity", "etf"),
        *,
        progress: ProgressOption = None,
    ) -> FetchResult:
        """Return a market snapshot with operational metadata."""

        return FetchResult.from_service(
            self._service.market_watch(tuple(instrument_types), reporter=self._reporter(progress))
        )

    def option_chain(self, underlying: str, *, progress: ProgressOption = None) -> pl.DataFrame:
        """Return one canonical row per put or call contract."""

        return self.fetch_option_chain(underlying, progress=progress).data

    def fetch_option_chain(
        self, underlying: str, *, progress: ProgressOption = None
    ) -> FetchResult:
        """Return option contracts with operational metadata."""

        return FetchResult.from_service(
            self._service.option_chain(underlying, reporter=self._reporter(progress))
        )

    def _reporter(self, option: ProgressOption):
        return make_progress_reporter(self._settings.progress if option is None else option)


class InstrumentNamespace:
    """Synchronous instrument discovery methods."""

    def __init__(self, service: InstrumentService, settings: Settings) -> None:
        self._service = service
        self._settings = settings

    def search(self, term: str, *, progress: ProgressOption = None) -> pl.DataFrame:
        """Search the canonical instrument master."""

        return self.fetch_search(term, progress=progress).data

    def fetch_search(self, term: str, *, progress: ProgressOption = None) -> FetchResult:
        """Search instruments and include source metadata."""

        reporter = make_progress_reporter(self._settings.progress if progress is None else progress)
        return FetchResult.from_service(self._service.search(term, reporter))


class IngestionNamespace:
    """Explicit persisted ingestion over configured storage."""

    def __init__(self, service: IngestionService, settings: Settings) -> None:
        self._service = service
        self._settings = settings

    def daily_prices(
        self,
        symbols: Sequence[str],
        start: date | str | None = None,
        end: date | str | None = None,
        *,
        progress: ProgressOption = None,
    ) -> IngestionRun:
        """Persist Bronze and Silver daily prices for each identifier."""

        return self._service.daily_prices(
            normalize_symbols(symbols),
            start=parse_date(start, "start"),
            end=parse_date(end, "end"),
            reporter=make_progress_reporter(
                self._settings.progress if progress is None else progress
            ),
        )

    def market_watch(
        self,
        instrument_types: Sequence[str] = ("equity", "etf"),
        *,
        progress: ProgressOption = None,
    ) -> IngestionRun:
        """Persist Bronze, Silver market watch, and Gold market snapshot."""

        return self._service.market_watch(
            tuple(instrument_types),
            reporter=make_progress_reporter(
                self._settings.progress if progress is None else progress
            ),
        )

    def option_chain(self, underlying: str, *, progress: ProgressOption = None) -> IngestionRun:
        """Persist Bronze, Silver option quotes, and a Gold option chain."""

        return self._service.option_chain(
            underlying,
            reporter=make_progress_reporter(
                self._settings.progress if progress is None else progress
            ),
        )


class Client:
    """Long-lived synchronous Oxtapus client."""

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        transport: SyncTransport | None = None,
        storage: StorageBackend | None = None,
    ) -> None:
        self.settings = settings or Settings()
        self._owns_transport = transport is None
        self._owns_storage = storage is None
        self._transport = transport or _transport(self.settings)
        self.storage = storage or _storage(self.settings)
        provider = TsetmcProvider(self._transport)
        resolver = InstrumentResolver(provider)
        self.market = MarketNamespace(
            MarketDataService(
                provider,
                resolver,
                concurrency=self.settings.concurrency,
                failure_mode=self.settings.failure_mode,
            ),
            self.settings,
        )
        self.instruments = InstrumentNamespace(InstrumentService(provider), self.settings)
        self.ingestion = IngestionNamespace(
            IngestionService(
                provider,
                resolver,
                self.storage,
                quality_policy=self.settings.quality_policy,
            ),
            self.settings,
        )
        self._provider = provider
        self._closed = False

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def close(self) -> None:
        """Close transport resources owned by this client."""

        if self._closed:
            return
        if self._owns_transport:
            self._transport.close()
        close_storage = getattr(self.storage, "close", None)
        if self._owns_storage and callable(close_storage):
            close_storage()
        self._closed = True

    @property
    def closed(self) -> bool:
        """Whether the client has been closed."""

        return self._closed

    def capabilities(self) -> tuple[ProviderCapability, ...]:
        """Return verified provider capabilities without network access."""

        return self._provider.capabilities()


def _transport(settings: Settings) -> Httpx2SyncTransport:
    return Httpx2SyncTransport(
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


def _storage(settings: Settings) -> StorageBackend:
    if settings.storage_backend == "memory":
        return MemoryStorage()
    if settings.storage_backend == "parquet":
        return LocalParquetStorage(settings.data_directory)
    return DuckDBStorage(settings.data_directory)


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
