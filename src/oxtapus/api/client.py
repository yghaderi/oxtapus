# ruff: noqa: RUF002
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
    AssetPriceService,
    GovernanceService,
    IngestionRun,
    IngestionService,
    InstrumentService,
    MarketDataService,
)
from oxtapus.domain.enums import ProviderCapability
from oxtapus.domain.errors import PartialFailureError, PartialFetchWarning
from oxtapus.progress.reporter import ProgressOption, make_progress_reporter
from oxtapus.providers.tgju.provider import TgjuProvider
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
    """متدهای همگام قیمت، تابلو، سفارش‌ها و بازار."""

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
        """برای ``symbols`` در بازهٔ تاریخ، دیتافریم قیمت روزانه برمی‌گرداند."""

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
        """قیمت روزانه را همراه metadata منبع، retry، خطا، کیفیت و lineage برمی‌گرداند."""

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
        """برای نوع ابزارهای خواسته‌شده، آخرین snapshot بازار را برمی‌گرداند."""

        return self.fetch_market_watch(instrument_types, progress=progress).data

    def fetch_market_watch(
        self,
        instrument_types: Sequence[str] = ("equity", "etf"),
        *,
        progress: ProgressOption = None,
    ) -> FetchResult:
        """snapshot بازار را همراه metadata عملیاتی برمی‌گرداند."""

        return FetchResult.from_service(
            self._service.market_watch(tuple(instrument_types), reporter=self._reporter(progress))
        )

    def quote(self, identifier: str, *, progress: ProgressOption = None) -> pl.DataFrame:
        """برای ``identifier``، دیتافریم تک‌ردیفی آخرین اطلاعات تابلو را برمی‌گرداند."""

        return self.fetch_quote(identifier, progress=progress).data

    def fetch_quote(self, identifier: str, *, progress: ProgressOption = None) -> FetchResult:
        """اطلاعات تابلو را همراه metadata عملیاتی برمی‌گرداند."""

        return FetchResult.from_service(
            self._service.quote(identifier, reporter=self._reporter(progress))
        )

    def market_depth(self, identifier: str, *, progress: ProgressOption = None) -> pl.DataFrame:
        """برای ``identifier``، حداکثر پنج سطح فعلی order book را برمی‌گرداند."""

        return self.fetch_market_depth(identifier, progress=progress).data

    def fetch_market_depth(
        self, identifier: str, *, progress: ProgressOption = None
    ) -> FetchResult:
        """سطح‌های order book را همراه metadata عملیاتی برمی‌گرداند."""

        return FetchResult.from_service(
            self._service.order_book(identifier, reporter=self._reporter(progress))
        )

    def investor_activity(
        self, identifier: str, *, progress: ProgressOption = None
    ) -> pl.DataFrame:
        """آمار فعلی خرید و فروش حقیقی و حقوقی ``identifier`` را برمی‌گرداند."""

        return self.fetch_investor_activity(identifier, progress=progress).data

    def fetch_investor_activity(
        self, identifier: str, *, progress: ProgressOption = None
    ) -> FetchResult:
        """آمار حقیقی/حقوقی را همراه metadata عملیاتی برمی‌گرداند."""

        return FetchResult.from_service(
            self._service.investor_activity(identifier, reporter=self._reporter(progress))
        )

    def option_chain(self, underlying: str, *, progress: ProgressOption = None) -> pl.DataFrame:
        """برای ``underlying``، یک ردیف canonical برای هر قرارداد اختیار برمی‌گرداند."""

        return self.fetch_option_chain(underlying, progress=progress).data

    def fetch_option_chain(
        self, underlying: str, *, progress: ProgressOption = None
    ) -> FetchResult:
        """قراردادهای اختیار را همراه metadata عملیاتی برمی‌گرداند."""

        return FetchResult.from_service(
            self._service.option_chain(underlying, reporter=self._reporter(progress))
        )

    def _reporter(self, option: ProgressOption):
        return make_progress_reporter(self._settings.progress if option is None else option)


class InstrumentNamespace:
    """متدهای همگام جست‌وجو، هویت و اطلاعات ابزار."""

    def __init__(self, service: InstrumentService, settings: Settings) -> None:
        self._service = service
        self._settings = settings

    def search(self, term: str, *, progress: ProgressOption = None) -> pl.DataFrame:
        """ابزارهای منطبق با ``term`` را در یک دیتافریم برمی‌گرداند."""

        return self.fetch_search(term, progress=progress).data

    def fetch_search(self, term: str, *, progress: ProgressOption = None) -> FetchResult:
        """نتیجهٔ جست‌وجو را همراه metadata منبع برمی‌گرداند."""

        reporter = make_progress_reporter(self._settings.progress if progress is None else progress)
        return FetchResult.from_service(self._service.search(term, reporter))

    def info(self, identifier: str, *, progress: ProgressOption = None) -> pl.DataFrame:
        """اطلاعات معاملاتی و ارزش‌گذاری ``identifier`` را برمی‌گرداند."""

        return self.fetch_info(identifier, progress=progress).data

    def fetch_info(self, identifier: str, *, progress: ProgressOption = None) -> FetchResult:
        """اطلاعات ابزار را همراه metadata عملیاتی برمی‌گرداند."""

        reporter = make_progress_reporter(self._settings.progress if progress is None else progress)
        return FetchResult.from_service(self._service.info(identifier, reporter))

    def identity(self, identifier: str, *, progress: ProgressOption = None) -> pl.DataFrame:
        """هویت، بازار، صنعت و زیرصنعت ``identifier`` را برمی‌گرداند."""

        return self.fetch_identity(identifier, progress=progress).data

    def fetch_identity(self, identifier: str, *, progress: ProgressOption = None) -> FetchResult:
        """هویت ابزار را همراه metadata عملیاتی برمی‌گرداند."""

        reporter = make_progress_reporter(self._settings.progress if progress is None else progress)
        return FetchResult.from_service(self._service.identity(identifier, reporter))


class GovernanceNamespace:
    """متدهای همگام افشاهای راهبری شرکتی."""

    def __init__(self, service: GovernanceService, settings: Settings) -> None:
        self._service = service
        self._settings = settings

    def board_members(self, identifier: str, *, progress: ProgressOption = None) -> pl.DataFrame:
        """تاریخچهٔ اعضای هیئت‌مدیرهٔ ``identifier`` را به‌شکل تخت برمی‌گرداند."""

        return self.fetch_board_members(identifier, progress=progress).data

    def fetch_board_members(
        self, identifier: str, *, progress: ProgressOption = None
    ) -> FetchResult:
        """تاریخچهٔ هیئت‌مدیره را همراه metadata عملیاتی برمی‌گرداند."""

        reporter = make_progress_reporter(self._settings.progress if progress is None else progress)
        return FetchResult.from_service(self._service.board_members(identifier, reporter))


class AssetNamespace:
    """متدهای همگام تاریخچهٔ ارز و سکه."""

    def __init__(self, service: AssetPriceService, settings: Settings) -> None:
        self._service = service
        self._settings = settings

    def history(
        self,
        asset: str,
        start: date | str | None = None,
        end: date | str | None = None,
        *,
        progress: ProgressOption = None,
    ) -> pl.DataFrame:
        """برای ``asset`` و بازهٔ تاریخ، دیتافریم روزانهٔ OHLC برمی‌گرداند."""

        return self.fetch_history(asset, start, end, progress=progress).data

    def fetch_history(
        self,
        asset: str,
        start: date | str | None = None,
        end: date | str | None = None,
        *,
        progress: ProgressOption = None,
    ) -> FetchResult:
        """تاریخچهٔ دارایی را همراه metadata منبع، کیفیت، retry و lineage برمی‌گرداند."""

        reporter = make_progress_reporter(self._settings.progress if progress is None else progress)
        return FetchResult.from_service(
            self._service.history(
                asset,
                start=parse_date(start, "start"),
                end=parse_date(end, "end"),
                reporter=reporter,
            )
        )


class IngestionNamespace:
    """دریافت و ذخیره‌سازی صریح در storage تنظیم‌شده."""

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
        """قیمت روزانهٔ ``symbols`` را در لایه‌های Bronze و Silver ذخیره می‌کند."""

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
        """دیده‌بان Bronze/Silver و snapshot لایهٔ Gold را ذخیره می‌کند."""

        return self._service.market_watch(
            tuple(instrument_types),
            reporter=make_progress_reporter(
                self._settings.progress if progress is None else progress
            ),
        )

    def option_chain(self, underlying: str, *, progress: ProgressOption = None) -> IngestionRun:
        """quoteهای اختیار Bronze/Silver و زنجیرهٔ Gold را ذخیره می‌کند."""

        return self._service.option_chain(
            underlying,
            reporter=make_progress_reporter(
                self._settings.progress if progress is None else progress
            ),
        )


class Client:
    """کلاینت همگام با اتصال قابل‌استفادهٔ مجدد و namespaceهای عمومی."""

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
        tgju_provider = TgjuProvider(self._transport)
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
        self.instruments = InstrumentNamespace(InstrumentService(provider, resolver), self.settings)
        self.governance = GovernanceNamespace(GovernanceService(provider, resolver), self.settings)
        self.assets = AssetNamespace(AssetPriceService(tgju_provider), self.settings)
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
        self._tgju_provider = tgju_provider
        self._closed = False

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def close(self) -> None:
        """منابع transport و storage متعلق به کلاینت را می‌بندد."""

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
        """اگر کلاینت بسته شده باشد ``True`` برمی‌گرداند."""

        return self._closed

    def capabilities(self) -> tuple[ProviderCapability, ...]:
        """قابلیت‌های تأییدشدهٔ providerها را بدون درخواست شبکه برمی‌گرداند."""

        return tuple(
            dict.fromkeys(self._provider.capabilities() + self._tgju_provider.capabilities())
        )


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
