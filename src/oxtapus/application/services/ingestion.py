"""Application service for replayable persisted ingestion."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date

from oxtapus.application.ingestion import IngestionPipeline, LayeredIngestionResult
from oxtapus.domain.instruments import Instrument
from oxtapus.progress.reporter import ProgressReporter
from oxtapus.providers.base import FetchFailure
from oxtapus.providers.tsetmc.provider import TsetmcProvider
from oxtapus.providers.tsetmc.queries import DailyPriceQuery, MarketWatchQuery, OptionChainQuery
from oxtapus.providers.tsetmc.resolver import InstrumentResolver
from oxtapus.storage.base import StorageBackend


@dataclass(frozen=True, slots=True)
class IngestionRun:
    """Successful layered writes and item-scoped ingestion failures."""

    results: tuple[LayeredIngestionResult, ...]
    failures: tuple[FetchFailure, ...]


class IngestionService:
    """Fetch and persist verified capabilities through provider and layer services."""

    def __init__(
        self,
        provider: TsetmcProvider,
        resolver: InstrumentResolver,
        storage: StorageBackend,
        *,
        quality_policy: str,
    ) -> None:
        self._provider = provider
        self._resolver = resolver
        self._storage = storage
        self._quality_policy = quality_policy

    def daily_prices(
        self,
        symbols: tuple[str, ...],
        *,
        start: date | None,
        end: date | None,
        reporter: ProgressReporter,
    ) -> IngestionRun:
        """Persist one Bronze and Silver result per resolved instrument."""

        results: list[LayeredIngestionResult] = []
        failures: list[FetchFailure] = []
        operation_id = uuid.uuid4().hex
        pipeline = IngestionPipeline(
            self._storage,
            self._provider.fetchers.daily,
            silver_dataset="daily_price",
            quality_policy=self._quality_policy,
        )
        for identifier in symbols:
            try:
                instrument = self._resolver.resolve(
                    identifier, reporter=reporter, operation_id=operation_id
                )
                execution = self._provider.daily_prices(
                    _daily_query(instrument, start, end),
                    reporter=reporter,
                    operation_id=operation_id,
                )
                results.append(pipeline.ingest(execution))
            except Exception as exc:
                failures.append(FetchFailure(identifier, type(exc).__name__, str(exc)))
        return IngestionRun(tuple(results), tuple(failures))

    def market_watch(
        self,
        instrument_types: tuple[str, ...],
        *,
        reporter: ProgressReporter,
    ) -> IngestionRun:
        """Persist one market-watch Bronze, Silver, and Gold snapshot."""

        operation_id = uuid.uuid4().hex
        execution = self._provider.market_watch(
            MarketWatchQuery(instrument_types=instrument_types),
            reporter=reporter,
            operation_id=operation_id,
        )
        pipeline = IngestionPipeline(
            self._storage,
            self._provider.fetchers.watch,
            silver_dataset="market_watch",
            gold_dataset="market_snapshot",
            quality_policy=self._quality_policy,
        )
        return IngestionRun((pipeline.ingest(execution),), ())

    def option_chain(
        self,
        underlying: str,
        *,
        reporter: ProgressReporter,
    ) -> IngestionRun:
        """Persist one option Bronze, Silver quote set, and Gold chain."""

        operation_id = uuid.uuid4().hex
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
        pipeline = IngestionPipeline(
            self._storage,
            self._provider.fetchers.options,
            silver_dataset="option_quote",
            gold_dataset="option_chain",
            quality_policy=self._quality_policy,
        )
        return IngestionRun((pipeline.ingest(execution),), ())


def _daily_query(instrument: Instrument, start: date | None, end: date | None) -> DailyPriceQuery:
    return DailyPriceQuery(
        tsetmc_instrument_code=instrument.tsetmc_instrument_code,
        symbol=instrument.symbol,
        isin=instrument.isin,
        start=start,
        end=end,
    )
