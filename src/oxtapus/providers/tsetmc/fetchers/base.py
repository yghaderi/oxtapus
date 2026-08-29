"""Shared mechanics for explicit TSETMC fetcher stages."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from oxtapus.providers.base import (
    AsyncFetchContext,
    EndpointSpec,
    FetchContext,
    FetchExecution,
    QueryModel,
    TransformOutput,
)
from oxtapus.transport.base import RawResponse, TransportRequest

Q = TypeVar("Q", bound=QueryModel)

_SOURCE_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.tsetmc.com/",
}


class BaseTsetmcFetcher(ABC, Generic[Q]):
    """Three-stage fetcher with native sync and async extraction."""

    def __init__(self, endpoint: EndpointSpec) -> None:
        self.endpoint = endpoint

    @abstractmethod
    def transform_query(self, query: Q) -> Q:
        """Validate and normalize caller input."""

    def extract(self, query: Q, context: FetchContext) -> RawResponse:
        """Perform only synchronous remote access."""

        return context.transport.request(
            self._request(query, context.operation_id), reporter=context.reporter
        )

    async def extract_async(self, query: Q, context: AsyncFetchContext) -> RawResponse:
        """Perform only asynchronous remote access."""

        return await context.transport.request(
            self._request(query, context.operation_id), reporter=context.reporter
        )

    @abstractmethod
    def transform(self, response: RawResponse, query: Q) -> TransformOutput:
        """Convert source data to canonical data without I/O."""

    @abstractmethod
    def _url(self, query: Q) -> str:
        """Build a catalog-constrained URL."""

    def _params(self, query: Q) -> dict[str, str | int | float | bool]:
        return {}

    def execute(self, query: Q, context: FetchContext) -> FetchExecution[Q]:
        """Execute transform-query, extract, and transform in order."""

        normalized = self.transform_query(query)
        response = self.extract(normalized, context)
        return FetchExecution(
            normalized, response, self.transform(response, normalized), self.endpoint
        )

    async def execute_async(self, query: Q, context: AsyncFetchContext) -> FetchExecution[Q]:
        """Execute transform-query, async extract, and transform in order."""

        normalized = self.transform_query(query)
        response = await self.extract_async(normalized, context)
        return FetchExecution(
            normalized, response, self.transform(response, normalized), self.endpoint
        )

    def _request(self, query: Q, operation_id: str) -> TransportRequest:
        return TransportRequest(
            method=self.endpoint.method,
            url=self._url(query),
            endpoint=self.endpoint.name,
            capability=self.endpoint.capability.value,
            operation_id=operation_id,
            params=self._params(query),
            headers=_SOURCE_HEADERS,
            idempotent=self.endpoint.retry_safe,
        )
