"""Provider, endpoint, query, fetcher, and metadata contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Generic, Protocol, TypeVar, runtime_checkable

import polars as pl
from pydantic import BaseModel, ConfigDict

from oxtapus.domain.enums import EndpointStatus, ProviderCapability
from oxtapus.progress.reporter import ProgressReporter
from oxtapus.transport.base import AsyncTransport, RawResponse, SyncTransport


class QueryModel(BaseModel):
    """Strict base class for public provider queries."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class EndpointSpec(BaseModel):
    """Versioned, live-verification record for one provider endpoint."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    capability: ProviderCapability
    host: str
    method: str
    path_template: str
    parameters: tuple[str, ...]
    response_envelope: str
    identifier_type: str
    supported_instrument_types: tuple[str, ...]
    source_schema_version: str
    canonical_dataset: str
    primary_key: tuple[str, ...]
    update_cadence: str
    pagination_behavior: str
    retry_safe: bool
    required_headers: tuple[str, ...]
    known_restrictions: str
    observed_response_size: int
    last_verified_timestamp: datetime
    schema_fingerprint: str
    status: EndpointStatus
    known_limitations: str

    @property
    def url_template(self) -> str:
        """Return the catalog-owned absolute URL template."""

        return self.host.rstrip("/") + "/" + self.path_template.lstrip("/")


@dataclass(frozen=True, slots=True)
class FetchContext:
    """Dependencies shared by one synchronous fetch stage."""

    provider: str
    transport: SyncTransport
    reporter: ProgressReporter
    operation_id: str


@dataclass(frozen=True, slots=True)
class AsyncFetchContext:
    """Dependencies shared by one asynchronous fetch stage."""

    provider: str
    transport: AsyncTransport
    reporter: ProgressReporter
    operation_id: str


@dataclass(frozen=True, slots=True)
class TransformOutput:
    """Canonical transform output plus explicit source-schema observations."""

    data: pl.DataFrame
    warnings: tuple[str, ...] = ()
    unknown_fields: tuple[str, ...] = ()


Q = TypeVar("Q", bound=QueryModel)


@dataclass(frozen=True, slots=True)
class FetchExecution(Generic[Q]):
    """All three fetcher stages and their source evidence."""

    query: Q
    response: RawResponse
    output: TransformOutput
    endpoint: EndpointSpec


@dataclass(frozen=True, slots=True)
class FetchFailure:
    """One failed batch item."""

    item: str
    error_type: str
    message: str
    retry_count: int = 0


@dataclass(frozen=True, slots=True)
class FetchMetadata:
    """Operational metadata for a canonical fetch."""

    requested_capability: ProviderCapability
    requested_provider: str
    endpoint_used: str
    fallback_used: bool
    fallback_reason: str | None
    retrieval_timestamp: datetime
    elapsed_seconds: float
    retry_count: int
    source_schema_version: str
    canonical_schema_version: str
    warnings: tuple[str, ...] = ()
    partial_failures: tuple[FetchFailure, ...] = ()


@runtime_checkable
class Provider(Protocol):
    """Capability-discoverable provider contract."""

    name: str

    def capabilities(self) -> tuple[ProviderCapability, ...]:
        """Return enabled capabilities."""

        ...


@runtime_checkable
class Fetcher(Protocol[Q]):
    """Explicit transform-query, extract, transform pipeline."""

    endpoint: EndpointSpec

    def transform_query(self, query: Q) -> Q:
        """Validate and normalize caller input."""

        ...

    def extract(self, query: Q, context: FetchContext) -> RawResponse:
        """Perform only source access."""

        ...

    def transform(self, response: RawResponse, query: Q) -> TransformOutput:
        """Convert source records to canonical records without I/O."""

        ...


@runtime_checkable
class AsyncFetcher(Protocol[Q]):
    """Asynchronous extraction with the same pure query and transform stages."""

    endpoint: EndpointSpec

    def transform_query(self, query: Q) -> Q:
        """Validate and normalize caller input."""

        ...

    async def extract(self, query: Q, context: AsyncFetchContext) -> RawResponse:
        """Perform only asynchronous source access."""

        ...

    def transform(self, response: RawResponse, query: Q) -> TransformOutput:
        """Convert source records to canonical records without I/O."""

        ...


@dataclass(slots=True)
class ProviderRegistry:
    """Small explicit provider registry with no global mutable singleton."""

    _providers: dict[str, Provider] = field(default_factory=dict)

    def register(self, provider: Provider) -> None:
        """Register or intentionally replace one provider instance."""

        self._providers[provider.name] = provider

    def get(self, name: str) -> Provider:
        """Return a registered provider."""

        return self._providers[name]

    def capabilities(
        self, provider: str | None = None
    ) -> dict[str, tuple[ProviderCapability, ...]]:
        """Discover enabled capabilities without remote access."""

        if provider is not None:
            item = self.get(provider)
            return {provider: item.capabilities()}
        return {name: item.capabilities() for name, item in sorted(self._providers.items())}
