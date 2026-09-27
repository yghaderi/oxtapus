"""TGJU asset-history fetcher with native sync and async extraction."""

from __future__ import annotations

from oxtapus.providers.base import (
    AsyncFetchContext,
    EndpointSpec,
    FetchContext,
    FetchExecution,
    TransformOutput,
)
from oxtapus.providers.tgju.assets import asset_by_code
from oxtapus.providers.tgju.queries import AssetPriceHistoryQuery
from oxtapus.providers.tgju.transformers import transform_asset_price_history
from oxtapus.transport.base import RawResponse, TransportRequest

_SOURCE_HEADERS = {
    "Accept": "application/json",
    "Referer": "https://www.tgju.org/",
}


class AssetPriceHistoryFetcher:
    """Fetch and canonicalize complete history for one verified asset."""

    def __init__(self, endpoint: EndpointSpec) -> None:
        self.endpoint = endpoint

    def transform_query(self, query: AssetPriceHistoryQuery) -> AssetPriceHistoryQuery:
        """Normalize aliases and validate the requested date range."""

        normalized = AssetPriceHistoryQuery.model_validate(query.model_dump())
        if normalized.start and normalized.end and normalized.start > normalized.end:
            raise ValueError("start must be on or before end")
        return normalized

    def execute(
        self, query: AssetPriceHistoryQuery, context: FetchContext
    ) -> FetchExecution[AssetPriceHistoryQuery]:
        """Execute validation, extraction, and deterministic transformation."""

        normalized = self.transform_query(query)
        response = context.transport.request(
            self._request(normalized, context.operation_id), reporter=context.reporter
        )
        return FetchExecution(
            normalized, response, self.transform(response, normalized), self.endpoint
        )

    async def execute_async(
        self, query: AssetPriceHistoryQuery, context: AsyncFetchContext
    ) -> FetchExecution[AssetPriceHistoryQuery]:
        """Execute the same pipeline with native asynchronous extraction."""

        normalized = self.transform_query(query)
        response = await context.transport.request(
            self._request(normalized, context.operation_id), reporter=context.reporter
        )
        return FetchExecution(
            normalized, response, self.transform(response, normalized), self.endpoint
        )

    def transform(self, response: RawResponse, query: AssetPriceHistoryQuery) -> TransformOutput:
        """Convert the source body without performing I/O."""

        return transform_asset_price_history(response.json(), query)

    def _request(self, query: AssetPriceHistoryQuery, operation_id: str) -> TransportRequest:
        asset = asset_by_code(query.asset)
        url = self.endpoint.url_template.format(source_item=asset.source_id)
        return TransportRequest(
            method=self.endpoint.method,
            url=url,
            endpoint=self.endpoint.name,
            capability=self.endpoint.capability.value,
            operation_id=operation_id,
            headers=_SOURCE_HEADERS,
            idempotent=self.endpoint.retry_safe,
        )
