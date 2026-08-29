"""HTTPX2 transport lifecycle, retries, status, and progress tests."""

from __future__ import annotations

import asyncio

import httpx2
import pytest

from oxtapus.domain.errors import HTTPResponseError, RetryExhaustedError
from oxtapus.progress.events import ProgressEventType, RetryScheduled, TransferAdvanced
from oxtapus.progress.reporter import make_progress_reporter
from oxtapus.transport.async_httpx2 import Httpx2AsyncTransport
from oxtapus.transport.base import TransportRequest
from oxtapus.transport.retry import RetryPolicy
from oxtapus.transport.sync_httpx2 import Httpx2SyncTransport


def request() -> TransportRequest:
    return TransportRequest("GET", "https://example.test/data", "test", "test", "operation")


def test_sync_transport_retries_only_failed_request_and_respects_metadata() -> None:
    calls = 0

    def handler(incoming: httpx2.Request) -> httpx2.Response:
        nonlocal calls
        calls += 1
        if calls < 3:
            return httpx2.Response(503, headers={"Retry-After": "0"}, request=incoming)
        return httpx2.Response(
            200,
            content=b'{"ok":true}',
            headers={"content-type": "application/json", "content-length": "11"},
            request=incoming,
        )

    client = httpx2.Client(transport=httpx2.MockTransport(handler))
    sleeps: list[float] = []
    events: list[ProgressEventType] = []
    transport = Httpx2SyncTransport(
        client=client,
        retry_policy=RetryPolicy(max_attempts=3, base_delay_seconds=0),
        requests_per_second=1000,
        sleep=sleeps.append,
        random_source=lambda: 0,
    )
    response = transport.request(request(), reporter=make_progress_reporter(events.append))
    transport.close()
    assert calls == 3
    assert response.retry_count == 2
    assert len([event for event in events if isinstance(event, RetryScheduled)]) == 2
    final = [event for event in events if isinstance(event, TransferAdvanced)][-1]
    assert final.percentage == 100
    assert sleeps == [0, 0]
    assert not client.is_closed
    client.close()


def test_sync_transport_does_not_retry_normal_client_error() -> None:
    calls = 0

    def handler(incoming: httpx2.Request) -> httpx2.Response:
        nonlocal calls
        calls += 1
        return httpx2.Response(404, request=incoming)

    client = httpx2.Client(transport=httpx2.MockTransport(handler))
    transport = Httpx2SyncTransport(client=client, requests_per_second=1000)
    with pytest.raises(HTTPResponseError) as caught:
        transport.request(request(), reporter=make_progress_reporter(False))
    assert caught.value.status_code == 404
    assert calls == 1
    client.close()


def test_sync_transport_reports_retry_exhaustion() -> None:
    def handler(incoming: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(503, request=incoming)

    client = httpx2.Client(transport=httpx2.MockTransport(handler))
    transport = Httpx2SyncTransport(
        client=client,
        retry_policy=RetryPolicy(max_attempts=2, base_delay_seconds=0),
        requests_per_second=1000,
        sleep=lambda _: None,
    )
    with pytest.raises(RetryExhaustedError) as caught:
        transport.request(request(), reporter=make_progress_reporter(False))
    assert caught.value.attempts == 2
    assert isinstance(caught.value.original, HTTPResponseError)
    client.close()


async def test_async_transport_retry_and_external_lifecycle() -> None:
    calls = 0

    async def handler(incoming: httpx2.Request) -> httpx2.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx2.Response(500, request=incoming)
        return httpx2.Response(
            200,
            content=b'{"ok":true}',
            headers={"content-type": "application/json"},
            request=incoming,
        )

    client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler))

    async def no_sleep(_: float) -> None:
        await asyncio.sleep(0)

    transport = Httpx2AsyncTransport(
        client=client,
        retry_policy=RetryPolicy(max_attempts=2, base_delay_seconds=0),
        requests_per_second=1000,
        sleep=no_sleep,
        random_source=lambda: 0,
    )
    response = await transport.request(request(), reporter=make_progress_reporter(False))
    await transport.aclose()
    assert response.retry_count == 1
    assert calls == 2
    assert not client.is_closed
    await client.aclose()


@pytest.mark.parametrize("status", [429, 500, 502, 504])
def test_retryable_status_matrix(status: int) -> None:
    calls = 0

    def handler(incoming: httpx2.Request) -> httpx2.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx2.Response(status, request=incoming)
        return httpx2.Response(
            200,
            content=b'{"ok":true}',
            headers={"content-type": "application/json"},
            request=incoming,
        )

    client = httpx2.Client(transport=httpx2.MockTransport(handler))
    transport = Httpx2SyncTransport(
        client=client,
        retry_policy=RetryPolicy(max_attempts=2, base_delay_seconds=0),
        requests_per_second=1000,
        sleep=lambda _: None,
    )
    assert transport.request(request(), reporter=make_progress_reporter(False)).retry_count == 1
    assert calls == 2
    client.close()


async def test_async_transport_propagates_cancellation() -> None:
    waiting = asyncio.Event()

    class SlowStream(httpx2.AsyncByteStream):
        async def __aiter__(self):
            waiting.set()
            await asyncio.Event().wait()
            yield b'{"ok":true}'

    async def handler(incoming: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(
            200,
            stream=SlowStream(),
            headers={"content-type": "application/json"},
            request=incoming,
        )

    client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
    transport = Httpx2AsyncTransport(client=client, requests_per_second=1000)
    task = asyncio.create_task(transport.request(request(), reporter=make_progress_reporter(False)))
    await waiting.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    await client.aclose()
