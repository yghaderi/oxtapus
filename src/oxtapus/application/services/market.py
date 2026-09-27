"""Capability-oriented market-data application services."""

from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable
from datetime import UTC, date, datetime
from typing import Any

import polars as pl

from oxtapus.application.batch import run_batch, run_batch_async
from oxtapus.application.results import ServiceResult
from oxtapus.data.lineage import Lineage, LineageNode
from oxtapus.data.quality import validate_daily_prices
from oxtapus.domain.enums import DataLayer, FailureMode, ProviderCapability
from oxtapus.progress.events import OperationCompleted, OperationStarted
from oxtapus.progress.reporter import ProgressReporter
from oxtapus.providers.base import FetchExecution
from oxtapus.providers.tsetmc.provider import AsyncTsetmcProvider, TsetmcProvider
from oxtapus.providers.tsetmc.queries import (
    DailyPriceQuery,
    InvestorActivityQuery,
    MarketWatchQuery,
    OptionChainQuery,
    OrderBookQuery,
    QuoteQuery,
)
from oxtapus.providers.tsetmc.resolver import AsyncInstrumentResolver, InstrumentResolver

_CANONICAL_VERSION = "1.0.0"


class MarketDataService:
    """Synchronous use cases over a capability-oriented provider."""

    def __init__(
        self,
        provider: TsetmcProvider,
        resolver: InstrumentResolver,
        *,
        concurrency: int,
        failure_mode: FailureMode,
    ) -> None:
        self._provider = provider
        self._resolver = resolver
        self._concurrency = concurrency
        self._failure_mode = failure_mode

    def daily_prices(
        self,
        symbols: tuple[str, ...],
        *,
        start: date | None,
        end: date | None,
        reporter: ProgressReporter,
    ) -> ServiceResult:
        """Resolve and retrieve multiple instruments with item-scoped failures."""

        operation_id = uuid.uuid4().hex
        started = time.monotonic()

        def fetch(identifier: str) -> FetchExecution[DailyPriceQuery]:
            instrument = self._resolver.resolve(
                identifier,
                reporter=reporter,
                operation_id=operation_id,
            )
            return self._provider.daily_prices(
                DailyPriceQuery(
                    tsetmc_instrument_code=instrument.tsetmc_instrument_code,
                    symbol=instrument.symbol,
                    isin=instrument.isin,
                    start=start,
                    end=end,
                ),
                reporter=reporter,
                operation_id=operation_id,
            )

        outcome = run_batch(
            symbols,
            fetch,
            capability=ProviderCapability.DAILY_PRICES.value,
            operation_id=operation_id,
            reporter=reporter,
            concurrency=self._concurrency,
            failure_mode=self._failure_mode,
        )
        frame = _concat([item.output.data for item in outcome.values])
        endpoint = self._provider.fetchers.daily.endpoint
        quality = validate_daily_prices(frame)
        return ServiceResult(
            data=frame,
            capability=ProviderCapability.DAILY_PRICES,
            provider=self._provider.name,
            endpoint=endpoint.name,
            query={"symbols": list(symbols), "start": start, "end": end},
            retrieved_at=_retrieved_at(outcome.values),
            elapsed=time.monotonic() - started,
            retry_count=sum(item.response.retry_count for item in outcome.values),
            warnings=_warnings(outcome.values),
            failures=outcome.failures,
            source_schema_version=endpoint.source_schema_version,
            canonical_schema_version=_CANONICAL_VERSION,
            data_layer=DataLayer.SILVER,
            lineage=_lineage(
                operation_id,
                "daily_price",
                "canonicalize_daily_prices",
                DataLayer.SILVER,
            ),
            quality_summary=quality.summary(),
        )

    def market_watch(
        self,
        instrument_types: tuple[str, ...],
        *,
        reporter: ProgressReporter,
    ) -> ServiceResult:
        """Retrieve one bulk canonical market snapshot."""

        query = MarketWatchQuery(instrument_types=instrument_types)
        return self._single(
            query.model_dump(mode="json"),
            ProviderCapability.MARKET_WATCH,
            "market_watch",
            "canonicalize_market_watch",
            reporter,
            lambda operation_id: self._provider.market_watch(
                query, reporter=reporter, operation_id=operation_id
            ),
        )

    def quote(self, identifier: str, *, reporter: ProgressReporter) -> ServiceResult:
        """Resolve one instrument and retrieve its latest board quote."""

        instrument = self._resolve(identifier, reporter)
        query = QuoteQuery(
            tsetmc_instrument_code=instrument.tsetmc_instrument_code,
            symbol=instrument.symbol,
        )
        return self._single(
            {"identifier": identifier},
            ProviderCapability.QUOTE,
            "quote",
            "canonicalize_quote",
            reporter,
            lambda operation_id: self._provider.quote(
                query, reporter=reporter, operation_id=operation_id
            ),
        )

    def order_book(self, identifier: str, *, reporter: ProgressReporter) -> ServiceResult:
        """Resolve one instrument and retrieve its latest order-book levels."""

        instrument = self._resolve(identifier, reporter)
        query = OrderBookQuery(
            tsetmc_instrument_code=instrument.tsetmc_instrument_code,
        )
        return self._single(
            {"identifier": identifier},
            ProviderCapability.ORDER_BOOK,
            "order_book",
            "canonicalize_order_book",
            reporter,
            lambda operation_id: self._provider.order_book(
                query, reporter=reporter, operation_id=operation_id
            ),
        )

    def investor_activity(self, identifier: str, *, reporter: ProgressReporter) -> ServiceResult:
        """Resolve one instrument and retrieve current investor-type activity."""

        instrument = self._resolve(identifier, reporter)
        query = InvestorActivityQuery(
            tsetmc_instrument_code=instrument.tsetmc_instrument_code,
            symbol=instrument.symbol,
        )
        return self._single(
            {"identifier": identifier},
            ProviderCapability.INVESTOR_ACTIVITY,
            "investor_activity",
            "canonicalize_investor_activity",
            reporter,
            lambda operation_id: self._provider.investor_activity(
                query, reporter=reporter, operation_id=operation_id
            ),
        )

    def option_chain(self, underlying: str, *, reporter: ProgressReporter) -> ServiceResult:
        """Resolve an underlying and retrieve its canonical option contracts."""

        operation_id = uuid.uuid4().hex
        started = time.monotonic()
        reporter.emit(
            OperationStarted(
                operation_id=operation_id,
                capability=ProviderCapability.OPTION_CHAIN.value,
                total_items=1,
            )
        )
        instrument = self._resolver.resolve(
            underlying, reporter=reporter, operation_id=operation_id
        )
        execution = self._provider.option_chain(
            OptionChainQuery(
                underlying_symbol=instrument.symbol,
                underlying_tsetmc_instrument_code=instrument.tsetmc_instrument_code,
            ),
            reporter=reporter,
            operation_id=operation_id,
        )
        reporter.emit(
            OperationCompleted(
                operation_id=operation_id,
                total=1,
                success_count=1,
                failure_count=0,
                retry_count=execution.response.retry_count,
            )
        )
        return _single_result(
            execution,
            query={"underlying": underlying},
            capability=ProviderCapability.OPTION_CHAIN,
            dataset="option_chain",
            operation="construct_option_chain",
            operation_id=operation_id,
            elapsed=time.monotonic() - started,
            provider=self._provider.name,
        )

    def _single(
        self,
        query: dict[str, Any],
        capability: ProviderCapability,
        dataset: str,
        operation: str,
        reporter: ProgressReporter,
        fetch: Callable[[str], FetchExecution[Any]],
    ) -> ServiceResult:
        operation_id = uuid.uuid4().hex
        started = time.monotonic()
        reporter.emit(
            OperationStarted(
                operation_id=operation_id,
                capability=capability.value,
                total_items=1,
            )
        )
        execution = fetch(operation_id)
        reporter.emit(
            OperationCompleted(
                operation_id=operation_id,
                total=1,
                success_count=1,
                failure_count=0,
                retry_count=execution.response.retry_count,
            )
        )
        return _single_result(
            execution,
            query=query,
            capability=capability,
            dataset=dataset,
            operation=operation,
            operation_id=operation_id,
            elapsed=time.monotonic() - started,
            provider=self._provider.name,
        )

    def _resolve(self, identifier: str, reporter: ProgressReporter):
        return self._resolver.resolve(
            identifier,
            reporter=reporter,
            operation_id=uuid.uuid4().hex,
        )


class AsyncMarketDataService:
    """Native asynchronous counterpart with the same canonical results."""

    def __init__(
        self,
        provider: AsyncTsetmcProvider,
        resolver: AsyncInstrumentResolver,
        *,
        concurrency: int,
        failure_mode: FailureMode,
    ) -> None:
        self._provider = provider
        self._resolver = resolver
        self._concurrency = concurrency
        self._failure_mode = failure_mode

    async def daily_prices(
        self,
        symbols: tuple[str, ...],
        *,
        start: date | None,
        end: date | None,
        reporter: ProgressReporter,
    ) -> ServiceResult:
        operation_id = uuid.uuid4().hex
        started = time.monotonic()

        async def fetch(identifier: str) -> FetchExecution[DailyPriceQuery]:
            instrument = await self._resolver.resolve(
                identifier,
                reporter=reporter,
                operation_id=operation_id,
            )
            return await self._provider.daily_prices(
                DailyPriceQuery(
                    tsetmc_instrument_code=instrument.tsetmc_instrument_code,
                    symbol=instrument.symbol,
                    isin=instrument.isin,
                    start=start,
                    end=end,
                ),
                reporter=reporter,
                operation_id=operation_id,
            )

        outcome = await run_batch_async(
            symbols,
            fetch,
            capability=ProviderCapability.DAILY_PRICES.value,
            operation_id=operation_id,
            reporter=reporter,
            concurrency=self._concurrency,
            failure_mode=self._failure_mode,
        )
        frame = _concat([item.output.data for item in outcome.values])
        endpoint = self._provider.fetchers.daily.endpoint
        return ServiceResult(
            data=frame,
            capability=ProviderCapability.DAILY_PRICES,
            provider=self._provider.name,
            endpoint=endpoint.name,
            query={"symbols": list(symbols), "start": start, "end": end},
            retrieved_at=_retrieved_at(outcome.values),
            elapsed=time.monotonic() - started,
            retry_count=sum(item.response.retry_count for item in outcome.values),
            warnings=_warnings(outcome.values),
            failures=outcome.failures,
            source_schema_version=endpoint.source_schema_version,
            canonical_schema_version=_CANONICAL_VERSION,
            data_layer=DataLayer.SILVER,
            lineage=_lineage(
                operation_id,
                "daily_price",
                "canonicalize_daily_prices",
                DataLayer.SILVER,
            ),
            quality_summary=validate_daily_prices(frame).summary(),
        )

    async def market_watch(
        self,
        instrument_types: tuple[str, ...],
        *,
        reporter: ProgressReporter,
    ) -> ServiceResult:
        query = MarketWatchQuery(instrument_types=instrument_types)
        operation_id = uuid.uuid4().hex
        started = time.monotonic()
        execution = await self._provider.market_watch(
            query, reporter=reporter, operation_id=operation_id
        )
        return _single_result(
            execution,
            query=query.model_dump(mode="json"),
            capability=ProviderCapability.MARKET_WATCH,
            dataset="market_snapshot",
            operation="canonicalize_market_watch",
            operation_id=operation_id,
            elapsed=time.monotonic() - started,
            provider=self._provider.name,
        )

    async def quote(self, identifier: str, *, reporter: ProgressReporter) -> ServiceResult:
        """Resolve one instrument and retrieve its latest board quote."""

        instrument = await self._resolve(identifier, reporter)
        query = QuoteQuery(
            tsetmc_instrument_code=instrument.tsetmc_instrument_code,
            symbol=instrument.symbol,
        )
        return await self._single(
            {"identifier": identifier},
            ProviderCapability.QUOTE,
            "quote",
            "canonicalize_quote",
            reporter,
            lambda operation_id: self._provider.quote(
                query, reporter=reporter, operation_id=operation_id
            ),
        )

    async def order_book(self, identifier: str, *, reporter: ProgressReporter) -> ServiceResult:
        """Resolve one instrument and retrieve its latest order-book levels."""

        instrument = await self._resolve(identifier, reporter)
        query = OrderBookQuery(
            tsetmc_instrument_code=instrument.tsetmc_instrument_code,
        )
        return await self._single(
            {"identifier": identifier},
            ProviderCapability.ORDER_BOOK,
            "order_book",
            "canonicalize_order_book",
            reporter,
            lambda operation_id: self._provider.order_book(
                query, reporter=reporter, operation_id=operation_id
            ),
        )

    async def investor_activity(
        self, identifier: str, *, reporter: ProgressReporter
    ) -> ServiceResult:
        """Resolve one instrument and retrieve current investor-type activity."""

        instrument = await self._resolve(identifier, reporter)
        query = InvestorActivityQuery(
            tsetmc_instrument_code=instrument.tsetmc_instrument_code,
            symbol=instrument.symbol,
        )
        return await self._single(
            {"identifier": identifier},
            ProviderCapability.INVESTOR_ACTIVITY,
            "investor_activity",
            "canonicalize_investor_activity",
            reporter,
            lambda operation_id: self._provider.investor_activity(
                query, reporter=reporter, operation_id=operation_id
            ),
        )

    async def option_chain(self, underlying: str, *, reporter: ProgressReporter) -> ServiceResult:
        operation_id = uuid.uuid4().hex
        started = time.monotonic()
        instrument = await self._resolver.resolve(
            underlying, reporter=reporter, operation_id=operation_id
        )
        execution = await self._provider.option_chain(
            OptionChainQuery(
                underlying_symbol=instrument.symbol,
                underlying_tsetmc_instrument_code=instrument.tsetmc_instrument_code,
            ),
            reporter=reporter,
            operation_id=operation_id,
        )
        return _single_result(
            execution,
            query={"underlying": underlying},
            capability=ProviderCapability.OPTION_CHAIN,
            dataset="option_chain",
            operation="construct_option_chain",
            operation_id=operation_id,
            elapsed=time.monotonic() - started,
            provider=self._provider.name,
        )

    async def _single(
        self,
        query: dict[str, Any],
        capability: ProviderCapability,
        dataset: str,
        operation: str,
        reporter: ProgressReporter,
        fetch: Callable[[str], Awaitable[FetchExecution[Any]]],
    ) -> ServiceResult:
        operation_id = uuid.uuid4().hex
        started = time.monotonic()
        reporter.emit(
            OperationStarted(
                operation_id=operation_id,
                capability=capability.value,
                total_items=1,
            )
        )
        execution = await fetch(operation_id)
        reporter.emit(
            OperationCompleted(
                operation_id=operation_id,
                total=1,
                success_count=1,
                failure_count=0,
                retry_count=execution.response.retry_count,
            )
        )
        return _single_result(
            execution,
            query=query,
            capability=capability,
            dataset=dataset,
            operation=operation,
            operation_id=operation_id,
            elapsed=time.monotonic() - started,
            provider=self._provider.name,
        )

    async def _resolve(self, identifier: str, reporter: ProgressReporter):
        return await self._resolver.resolve(
            identifier,
            reporter=reporter,
            operation_id=uuid.uuid4().hex,
        )


def _single_result(
    execution: FetchExecution[Any],
    *,
    query: dict[str, Any],
    capability: ProviderCapability,
    dataset: str,
    operation: str,
    operation_id: str,
    elapsed: float,
    provider: str,
) -> ServiceResult:
    return ServiceResult(
        data=execution.output.data,
        capability=capability,
        provider=provider,
        endpoint=execution.endpoint.name,
        query=query,
        retrieved_at=execution.response.retrieved_at,
        elapsed=elapsed,
        retry_count=execution.response.retry_count,
        warnings=execution.output.warnings
        + tuple(
            f"Unknown additive source field: {field}" for field in execution.output.unknown_fields
        ),
        failures=(),
        source_schema_version=execution.endpoint.source_schema_version,
        canonical_schema_version=_CANONICAL_VERSION,
        data_layer=(
            DataLayer.GOLD if capability is ProviderCapability.OPTION_CHAIN else DataLayer.SILVER
        ),
        lineage=_lineage(
            operation_id,
            dataset,
            operation,
            DataLayer.GOLD if capability is ProviderCapability.OPTION_CHAIN else DataLayer.SILVER,
        ),
        quality_summary={
            "checked_rows": execution.output.data.height,
            "accepted_rows": execution.output.data.height,
            "quarantined_rows": 0,
            "issue_count": 0,
            "passed": True,
        },
    )


def _lineage(run_id: str, dataset: str, operation: str, layer: DataLayer) -> Lineage:
    return Lineage(
        run_id,
        (
            LineageNode(
                dataset=dataset,
                layer=layer,
                schema_version=_CANONICAL_VERSION,
                operation=operation,
            ),
        ),
    )


def _retrieved_at(executions: tuple[FetchExecution[Any], ...]) -> datetime:
    if not executions:
        return datetime.now(UTC)
    return max(item.response.retrieved_at for item in executions)


def _warnings(executions: tuple[FetchExecution[Any], ...]) -> tuple[str, ...]:
    warnings: set[str] = set()
    for item in executions:
        warnings.update(item.output.warnings)
        warnings.update(
            f"Unknown additive source field: {name}" for name in item.output.unknown_fields
        )
    return tuple(sorted(warnings))


def _concat(frames: list[pl.DataFrame]) -> pl.DataFrame:
    if not frames:
        return pl.DataFrame(
            schema={
                "isin": pl.String,
                "symbol": pl.String,
                "tsetmc_instrument_code": pl.String,
                "trading_date": pl.Date,
                "open_price": pl.Int64,
                "high_price": pl.Int64,
                "low_price": pl.Int64,
                "close_price": pl.Int64,
                "last_price": pl.Int64,
                "previous_close_price": pl.Int64,
                "price_change": pl.Float64,
                "trade_count": pl.Int64,
                "trade_volume": pl.Int64,
                "trade_value": pl.Int64,
            }
        )
    return pl.concat(frames, how="vertical_relaxed").sort(
        ["tsetmc_instrument_code", "trading_date"]
    )
