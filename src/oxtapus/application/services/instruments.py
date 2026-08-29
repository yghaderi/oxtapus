"""Instrument discovery application services."""

from __future__ import annotations

import time
import uuid

from oxtapus.application.results import ServiceResult
from oxtapus.data.lineage import Lineage, LineageNode
from oxtapus.domain.enums import DataLayer, ProviderCapability
from oxtapus.progress.reporter import ProgressReporter
from oxtapus.providers.base import FetchExecution
from oxtapus.providers.tsetmc.provider import AsyncTsetmcProvider, TsetmcProvider
from oxtapus.providers.tsetmc.queries import InstrumentSearchQuery


class InstrumentService:
    """Synchronous instrument discovery."""

    def __init__(self, provider: TsetmcProvider) -> None:
        self._provider = provider

    def search(self, term: str, reporter: ProgressReporter) -> ServiceResult:
        operation_id = uuid.uuid4().hex
        started = time.monotonic()
        execution = self._provider.search(
            InstrumentSearchQuery(term=term), reporter=reporter, operation_id=operation_id
        )
        return _result(execution, term, operation_id, time.monotonic() - started)


class AsyncInstrumentService:
    """Native asynchronous instrument discovery."""

    def __init__(self, provider: AsyncTsetmcProvider) -> None:
        self._provider = provider

    async def search(self, term: str, reporter: ProgressReporter) -> ServiceResult:
        operation_id = uuid.uuid4().hex
        started = time.monotonic()
        execution = await self._provider.search(
            InstrumentSearchQuery(term=term), reporter=reporter, operation_id=operation_id
        )
        return _result(execution, term, operation_id, time.monotonic() - started)


def _result(
    execution: FetchExecution[InstrumentSearchQuery],
    term: str,
    operation_id: str,
    elapsed: float,
) -> ServiceResult:
    frame = execution.output.data
    return ServiceResult(
        data=frame,
        capability=ProviderCapability.INSTRUMENT_SEARCH,
        provider="tsetmc",
        endpoint=execution.endpoint.name,
        query={"term": term},
        retrieved_at=execution.response.retrieved_at,
        elapsed=elapsed,
        retry_count=execution.response.retry_count,
        warnings=execution.output.warnings,
        failures=(),
        source_schema_version=execution.endpoint.source_schema_version,
        canonical_schema_version="1.0.0",
        data_layer=DataLayer.SILVER,
        lineage=Lineage(
            operation_id,
            (
                LineageNode(
                    dataset="instrument",
                    layer=DataLayer.SILVER,
                    schema_version="1.0.0",
                    operation="canonicalize_instrument_search",
                ),
            ),
        ),
        quality_summary={
            "checked_rows": frame.height,
            "accepted_rows": frame.height,
            "quarantined_rows": 0,
            "issue_count": 0,
            "passed": True,
        },
    )
