"""Corporate-governance disclosure application services."""

from __future__ import annotations

import time
import uuid

from oxtapus.application.results import ServiceResult
from oxtapus.data.lineage import Lineage, LineageNode
from oxtapus.domain.enums import DataLayer, ProviderCapability
from oxtapus.progress.reporter import ProgressReporter
from oxtapus.providers.base import FetchExecution
from oxtapus.providers.tsetmc.provider import AsyncTsetmcProvider, TsetmcProvider
from oxtapus.providers.tsetmc.queries import BoardMembersQuery
from oxtapus.providers.tsetmc.resolver import AsyncInstrumentResolver, InstrumentResolver


class GovernanceService:
    """Synchronous corporate-governance use cases."""

    def __init__(self, provider: TsetmcProvider, resolver: InstrumentResolver) -> None:
        self._provider = provider
        self._resolver = resolver

    def board_members(self, identifier: str, reporter: ProgressReporter) -> ServiceResult:
        """Resolve an instrument and retrieve its board-member disclosure history."""

        operation_id = uuid.uuid4().hex
        started = time.monotonic()
        instrument = self._resolver.resolve(
            identifier, reporter=reporter, operation_id=operation_id
        )
        execution = self._provider.board_members(
            BoardMembersQuery(
                tsetmc_instrument_code=instrument.tsetmc_instrument_code,
                symbol=instrument.symbol,
            ),
            reporter=reporter,
            operation_id=operation_id,
        )
        return _result(execution, identifier, operation_id, time.monotonic() - started)


class AsyncGovernanceService:
    """Native asynchronous corporate-governance use cases."""

    def __init__(self, provider: AsyncTsetmcProvider, resolver: AsyncInstrumentResolver) -> None:
        self._provider = provider
        self._resolver = resolver

    async def board_members(self, identifier: str, reporter: ProgressReporter) -> ServiceResult:
        """Resolve an instrument and retrieve its board-member disclosure history."""

        operation_id = uuid.uuid4().hex
        started = time.monotonic()
        instrument = await self._resolver.resolve(
            identifier, reporter=reporter, operation_id=operation_id
        )
        execution = await self._provider.board_members(
            BoardMembersQuery(
                tsetmc_instrument_code=instrument.tsetmc_instrument_code,
                symbol=instrument.symbol,
            ),
            reporter=reporter,
            operation_id=operation_id,
        )
        return _result(execution, identifier, operation_id, time.monotonic() - started)


def _result(
    execution: FetchExecution[BoardMembersQuery],
    identifier: str,
    operation_id: str,
    elapsed: float,
) -> ServiceResult:
    frame = execution.output.data
    return ServiceResult(
        data=frame,
        capability=ProviderCapability.BOARD_MEMBERS,
        provider="tsetmc",
        endpoint=execution.endpoint.name,
        query={"identifier": identifier},
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
                    dataset="board_member_history",
                    layer=DataLayer.SILVER,
                    schema_version="1.0.0",
                    operation="parse_board_member_disclosures",
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
