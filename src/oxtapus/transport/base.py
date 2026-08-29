"""Transport protocols and response types."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol, runtime_checkable

from oxtapus.domain.errors import ResponseValidationError
from oxtapus.progress.reporter import ProgressReporter


@dataclass(frozen=True, slots=True)
class TransportRequest:
    """Provider-neutral description of one idempotent remote request."""

    method: str
    url: str
    endpoint: str
    capability: str
    operation_id: str
    params: dict[str, str | int | float | bool] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    idempotent: bool = True


@dataclass(frozen=True, slots=True)
class RawResponse:
    """A completely consumed source response with transport metadata."""

    request_id: str
    operation_id: str
    endpoint: str
    capability: str
    url: str
    status_code: int
    headers: dict[str, str]
    content: bytes
    retrieved_at: datetime
    elapsed_seconds: float
    retry_count: int

    def json(self) -> Any:
        """Decode JSON, translating parser failures into a public error."""

        try:
            return json.loads(self.content)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ResponseValidationError(
                f"Endpoint {self.endpoint!r} returned malformed JSON."
            ) from exc


@runtime_checkable
class SyncTransport(Protocol):
    """Native synchronous transport contract."""

    def request(self, request: TransportRequest, *, reporter: ProgressReporter) -> RawResponse:
        """Execute and completely consume one request."""

        ...

    def close(self) -> None:
        """Release owned resources."""

        ...


@runtime_checkable
class AsyncTransport(Protocol):
    """Native asynchronous transport contract."""

    async def request(
        self, request: TransportRequest, *, reporter: ProgressReporter
    ) -> RawResponse:
        """Execute and completely consume one request."""

        ...

    async def aclose(self) -> None:
        """Release owned resources."""

        ...


_SENSITIVE_HEADERS = frozenset(
    {"authorization", "cookie", "set-cookie", "proxy-authorization", "x-api-key"}
)


def sanitized_headers(headers: dict[str, str]) -> dict[str, str]:
    """Remove credentials and tracking values before metadata persistence."""

    return {
        key.lower(): value
        for key, value in headers.items()
        if key.lower() not in _SENSITIVE_HEADERS
    }
