"""Non-security asset-price application services."""

from __future__ import annotations

import time
import uuid
from datetime import date

from oxtapus.application.results import ServiceResult
from oxtapus.data.lineage import Lineage, LineageNode
from oxtapus.data.quality import validate_asset_prices
from oxtapus.domain.enums import DataLayer, ProviderCapability
from oxtapus.progress.events import OperationCompleted, OperationStarted
from oxtapus.progress.reporter import ProgressReporter
from oxtapus.providers.base import FetchExecution
from oxtapus.providers.tgju.provider import AsyncTgjuProvider, TgjuProvider
from oxtapus.providers.tgju.queries import AssetPriceHistoryQuery


class AssetPriceService:
    """Synchronous asset-price use cases."""

    def __init__(self, provider: TgjuProvider) -> None:
        self._provider = provider

    def history(
        self,
        asset: str,
        *,
        start: date | None,
        end: date | None,
        reporter: ProgressReporter,
    ) -> ServiceResult:
        """Retrieve canonical daily history for one supported asset."""

        operation_id = uuid.uuid4().hex
        started = time.monotonic()
        query = AssetPriceHistoryQuery(asset=asset, start=start, end=end)
        reporter.emit(
            OperationStarted(
                operation_id=operation_id,
                capability=ProviderCapability.ASSET_PRICE_HISTORY.value,
                total_items=1,
            )
        )
        execution = self._provider.asset_price_history(
            query, reporter=reporter, operation_id=operation_id
        )
        _complete(reporter, operation_id, execution)
        return _result(execution, query, operation_id, time.monotonic() - started)


class AsyncAssetPriceService:
    """Native asynchronous asset-price use cases."""

    def __init__(self, provider: AsyncTgjuProvider) -> None:
        self._provider = provider

    async def history(
        self,
        asset: str,
        *,
        start: date | None,
        end: date | None,
        reporter: ProgressReporter,
    ) -> ServiceResult:
        """Retrieve canonical daily history without blocking the event loop."""

        operation_id = uuid.uuid4().hex
        started = time.monotonic()
        query = AssetPriceHistoryQuery(asset=asset, start=start, end=end)
        reporter.emit(
            OperationStarted(
                operation_id=operation_id,
                capability=ProviderCapability.ASSET_PRICE_HISTORY.value,
                total_items=1,
            )
        )
        execution = await self._provider.asset_price_history(
            query, reporter=reporter, operation_id=operation_id
        )
        _complete(reporter, operation_id, execution)
        return _result(execution, query, operation_id, time.monotonic() - started)


def _complete(
    reporter: ProgressReporter,
    operation_id: str,
    execution: FetchExecution[AssetPriceHistoryQuery],
) -> None:
    reporter.emit(
        OperationCompleted(
            operation_id=operation_id,
            total=1,
            success_count=1,
            failure_count=0,
            retry_count=execution.response.retry_count,
        )
    )


def _result(
    execution: FetchExecution[AssetPriceHistoryQuery],
    query: AssetPriceHistoryQuery,
    operation_id: str,
    elapsed: float,
) -> ServiceResult:
    frame = execution.output.data
    quality = validate_asset_prices(frame)
    return ServiceResult(
        data=frame,
        capability=ProviderCapability.ASSET_PRICE_HISTORY,
        provider="tgju",
        endpoint=execution.endpoint.name,
        query=query.model_dump(mode="json"),
        retrieved_at=execution.response.retrieved_at,
        elapsed=elapsed,
        retry_count=execution.response.retry_count,
        warnings=execution.output.warnings
        + tuple(
            f"Unknown additive source field: {field}" for field in execution.output.unknown_fields
        ),
        failures=(),
        source_schema_version=execution.endpoint.source_schema_version,
        canonical_schema_version="1.0.0",
        data_layer=DataLayer.SILVER,
        lineage=Lineage(
            operation_id,
            (
                LineageNode(
                    dataset="asset_price_history",
                    layer=DataLayer.SILVER,
                    schema_version="1.0.0",
                    operation="canonicalize_asset_price_history",
                ),
            ),
        ),
        quality_summary=quality.summary(),
    )
