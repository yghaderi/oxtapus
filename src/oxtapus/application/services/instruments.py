"""Instrument discovery application services."""

from __future__ import annotations

import time
import uuid
from typing import Any

from oxtapus.application.results import ServiceResult
from oxtapus.data.lineage import Lineage, LineageNode
from oxtapus.domain.enums import DataLayer, ProviderCapability
from oxtapus.progress.reporter import ProgressReporter
from oxtapus.providers.base import FetchExecution
from oxtapus.providers.tsetmc.provider import AsyncTsetmcProvider, TsetmcProvider
from oxtapus.providers.tsetmc.queries import (
    InstrumentIdentityQuery,
    InstrumentInfoQuery,
    InstrumentSearchQuery,
)
from oxtapus.providers.tsetmc.resolver import AsyncInstrumentResolver, InstrumentResolver


class InstrumentService:
    """Synchronous instrument discovery."""

    def __init__(self, provider: TsetmcProvider, resolver: InstrumentResolver) -> None:
        self._provider = provider
        self._resolver = resolver

    def search(self, term: str, reporter: ProgressReporter) -> ServiceResult:
        operation_id = uuid.uuid4().hex
        started = time.monotonic()
        execution = self._provider.search(
            InstrumentSearchQuery(term=term), reporter=reporter, operation_id=operation_id
        )
        return _result(
            execution,
            query={"term": term},
            capability=ProviderCapability.INSTRUMENT_SEARCH,
            dataset="instrument",
            operation="canonicalize_instrument_search",
            operation_id=operation_id,
            elapsed=time.monotonic() - started,
        )

    def info(self, identifier: str, reporter: ProgressReporter) -> ServiceResult:
        """Resolve an identifier and retrieve its detailed instrument information."""

        operation_id = uuid.uuid4().hex
        started = time.monotonic()
        instrument = self._resolver.resolve(
            identifier, reporter=reporter, operation_id=operation_id
        )
        execution = self._provider.info(
            InstrumentInfoQuery(
                tsetmc_instrument_code=instrument.tsetmc_instrument_code,
            ),
            reporter=reporter,
            operation_id=operation_id,
        )
        return _result(
            execution,
            query={"identifier": identifier},
            capability=ProviderCapability.INSTRUMENT_MASTER,
            dataset="instrument_info",
            operation="canonicalize_instrument_info",
            operation_id=operation_id,
            elapsed=time.monotonic() - started,
        )

    def identity(self, identifier: str, reporter: ProgressReporter) -> ServiceResult:
        """Resolve an identifier and retrieve source identity and classification."""

        operation_id = uuid.uuid4().hex
        started = time.monotonic()
        instrument = self._resolver.resolve(
            identifier, reporter=reporter, operation_id=operation_id
        )
        execution = self._provider.identity(
            InstrumentIdentityQuery(
                tsetmc_instrument_code=instrument.tsetmc_instrument_code,
            ),
            reporter=reporter,
            operation_id=operation_id,
        )
        return _result(
            execution,
            query={"identifier": identifier},
            capability=ProviderCapability.INSTRUMENT_MASTER,
            dataset="instrument_identity",
            operation="canonicalize_instrument_identity",
            operation_id=operation_id,
            elapsed=time.monotonic() - started,
        )


class AsyncInstrumentService:
    """Native asynchronous instrument discovery."""

    def __init__(self, provider: AsyncTsetmcProvider, resolver: AsyncInstrumentResolver) -> None:
        self._provider = provider
        self._resolver = resolver

    async def search(self, term: str, reporter: ProgressReporter) -> ServiceResult:
        operation_id = uuid.uuid4().hex
        started = time.monotonic()
        execution = await self._provider.search(
            InstrumentSearchQuery(term=term), reporter=reporter, operation_id=operation_id
        )
        return _result(
            execution,
            query={"term": term},
            capability=ProviderCapability.INSTRUMENT_SEARCH,
            dataset="instrument",
            operation="canonicalize_instrument_search",
            operation_id=operation_id,
            elapsed=time.monotonic() - started,
        )

    async def info(self, identifier: str, reporter: ProgressReporter) -> ServiceResult:
        """Resolve an identifier and retrieve detailed instrument information."""

        operation_id = uuid.uuid4().hex
        started = time.monotonic()
        instrument = await self._resolver.resolve(
            identifier, reporter=reporter, operation_id=operation_id
        )
        execution = await self._provider.info(
            InstrumentInfoQuery(
                tsetmc_instrument_code=instrument.tsetmc_instrument_code,
            ),
            reporter=reporter,
            operation_id=operation_id,
        )
        return _result(
            execution,
            query={"identifier": identifier},
            capability=ProviderCapability.INSTRUMENT_MASTER,
            dataset="instrument_info",
            operation="canonicalize_instrument_info",
            operation_id=operation_id,
            elapsed=time.monotonic() - started,
        )

    async def identity(self, identifier: str, reporter: ProgressReporter) -> ServiceResult:
        """Resolve an identifier and retrieve source identity and classification."""

        operation_id = uuid.uuid4().hex
        started = time.monotonic()
        instrument = await self._resolver.resolve(
            identifier, reporter=reporter, operation_id=operation_id
        )
        execution = await self._provider.identity(
            InstrumentIdentityQuery(
                tsetmc_instrument_code=instrument.tsetmc_instrument_code,
            ),
            reporter=reporter,
            operation_id=operation_id,
        )
        return _result(
            execution,
            query={"identifier": identifier},
            capability=ProviderCapability.INSTRUMENT_MASTER,
            dataset="instrument_identity",
            operation="canonicalize_instrument_identity",
            operation_id=operation_id,
            elapsed=time.monotonic() - started,
        )


def _result(
    execution: FetchExecution[Any],
    *,
    query: dict[str, Any],
    capability: ProviderCapability,
    dataset: str,
    operation: str,
    operation_id: str,
    elapsed: float,
) -> ServiceResult:
    frame = execution.output.data
    return ServiceResult(
        data=frame,
        capability=capability,
        provider="tsetmc",
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
        canonical_schema_version="1.0.0",
        data_layer=DataLayer.SILVER,
        lineage=Lineage(
            operation_id,
            (
                LineageNode(
                    dataset=dataset,
                    layer=DataLayer.SILVER,
                    schema_version="1.0.0",
                    operation=operation,
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
