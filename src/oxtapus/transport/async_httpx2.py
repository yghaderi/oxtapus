"""Native asynchronous HTTPX2 transport."""

from __future__ import annotations

import asyncio
import random
import time
import uuid
from collections.abc import Awaitable, Callable, Mapping
from datetime import UTC, datetime
from typing import Any

import httpx2

from oxtapus.domain.errors import HTTPResponseError, RetryExhaustedError, TransportError
from oxtapus.progress.events import RetryScheduled, TransferAdvanced, TransferStarted
from oxtapus.progress.reporter import ProgressReporter
from oxtapus.transport.base import RawResponse, TransportRequest, sanitized_headers
from oxtapus.transport.rate_limit import AsyncHostRateLimiter
from oxtapus.transport.response import validate_response_body
from oxtapus.transport.retry import RetryPolicy


class Httpx2AsyncTransport:
    """Long-lived asynchronous HTTPX2 client with cancellation-safe retries."""

    def __init__(
        self,
        *,
        client: httpx2.AsyncClient | None = None,
        connect_timeout: float = 5.0,
        read_timeout: float = 30.0,
        write_timeout: float = 10.0,
        pool_timeout: float = 5.0,
        max_connections: int = 10,
        max_keepalive_connections: int = 5,
        http2: bool = False,
        verify: bool = True,
        proxy: str | None = None,
        follow_redirects: bool = False,
        user_agent: str = "Oxtapus/1.0",
        retry_policy: RetryPolicy | None = None,
        requests_per_second: float = 2.0,
        event_hooks: Mapping[str, list[Callable[..., Any]]] | None = None,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        random_source: Callable[[], float] = random.random,
    ) -> None:
        self._owns_client = client is None
        self._client = client or httpx2.AsyncClient(
            timeout=httpx2.Timeout(
                connect=connect_timeout,
                read=read_timeout,
                write=write_timeout,
                pool=pool_timeout,
            ),
            limits=httpx2.Limits(
                max_connections=max_connections,
                max_keepalive_connections=max_keepalive_connections,
            ),
            http1=True,
            http2=http2,
            verify=verify,
            proxy=proxy,
            follow_redirects=follow_redirects,
            headers={"User-Agent": user_agent},
            event_hooks=event_hooks,
        )
        self._retry_policy = retry_policy or RetryPolicy()
        self._limiter = AsyncHostRateLimiter(requests_per_second)
        self._sleep = sleep
        self._random_source = random_source
        self._closed = False

    @property
    def closed(self) -> bool:
        """Whether this transport has been closed."""

        return self._closed

    async def __aenter__(self) -> Httpx2AsyncTransport:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()

    async def request(
        self, request: TransportRequest, *, reporter: ProgressReporter
    ) -> RawResponse:
        """Execute one request without taking ownership of the caller's event loop."""

        if self._closed:
            raise TransportError("The transport is closed.")
        request_id = uuid.uuid4().hex
        accumulated_delay = 0.0
        for attempt in range(1, self._retry_policy.max_attempts + 1):
            await self._limiter.acquire()
            started = time.monotonic()
            retry_after: str | None = None
            try:
                async with self._client.stream(
                    request.method,
                    request.url,
                    params=request.params,
                    headers=request.headers,
                ) as response:
                    retry_after = response.headers.get("retry-after")
                    self._raise_for_status(response)
                    total = _content_length(response.headers.get("content-length"))
                    reporter.emit(
                        TransferStarted(
                            operation_id=request.operation_id,
                            request_id=request_id,
                            endpoint=request.endpoint,
                            total_bytes=total,
                        )
                    )
                    chunks: list[bytes] = []
                    downloaded = 0
                    transfer_started = time.monotonic()
                    async for chunk in response.aiter_bytes():
                        chunks.append(chunk)
                        downloaded += len(chunk)
                        elapsed = max(time.monotonic() - transfer_started, 1e-9)
                        reporter.emit(
                            TransferAdvanced(
                                operation_id=request.operation_id,
                                request_id=request_id,
                                downloaded_bytes=downloaded,
                                total_bytes=total,
                                bytes_per_second=downloaded / elapsed,
                            )
                        )
                    content = b"".join(chunks)
                    validate_response_body(content, response.headers.get("content-type"))
                    elapsed = max(time.monotonic() - transfer_started, 1e-9)
                    reporter.emit(
                        TransferAdvanced(
                            operation_id=request.operation_id,
                            request_id=request_id,
                            downloaded_bytes=downloaded,
                            total_bytes=total,
                            bytes_per_second=downloaded / elapsed,
                            complete=True,
                        )
                    )
                    return RawResponse(
                        request_id=request_id,
                        operation_id=request.operation_id,
                        endpoint=request.endpoint,
                        capability=request.capability,
                        url=str(response.url),
                        status_code=response.status_code,
                        headers=sanitized_headers(dict(response.headers)),
                        content=content,
                        retrieved_at=datetime.now(UTC),
                        elapsed_seconds=time.monotonic() - started,
                        retry_count=attempt - 1,
                    )
            except Exception as exc:
                if not self._is_retryable(exc, request.idempotent):
                    if isinstance(exc, (HTTPResponseError, TransportError)):
                        raise
                    if isinstance(exc, httpx2.TransportError):
                        raise TransportError(str(exc)) from exc
                    raise
                if attempt >= self._retry_policy.max_attempts:
                    raise RetryExhaustedError(attempt, exc) from exc
                delay = self._retry_policy.delay(
                    attempt,
                    retry_after=retry_after,
                    random_source=self._random_source,
                )
                if accumulated_delay + delay > self._retry_policy.max_total_delay_seconds:
                    raise RetryExhaustedError(attempt, exc) from exc
                accumulated_delay += delay
                reporter.emit(
                    RetryScheduled(
                        operation_id=request.operation_id,
                        request_id=request_id,
                        endpoint=request.endpoint,
                        attempt=attempt,
                        delay_seconds=delay,
                        reason=str(exc),
                    )
                )
                await self._sleep(delay)
        raise AssertionError("unreachable")

    async def aclose(self) -> None:
        """Close only clients owned by this transport."""

        if self._closed:
            return
        if self._owns_client:
            await self._client.aclose()
        self._closed = True

    def _is_retryable(self, exc: Exception, idempotent: bool) -> bool:
        if not idempotent:
            return False
        if isinstance(exc, HTTPResponseError):
            return exc.status_code in self._retry_policy.retry_status_codes
        return isinstance(exc, httpx2.TransportError)

    @staticmethod
    def _raise_for_status(response: httpx2.Response) -> None:
        try:
            response.raise_for_status()
        except httpx2.HTTPStatusError as exc:
            raise HTTPResponseError(
                response.status_code, str(response.url), response.reason_phrase
            ) from exc


def _content_length(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        length = int(value)
    except ValueError:
        return None
    return length if length >= 0 else None
