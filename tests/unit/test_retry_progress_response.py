"""Retry, progress, response, and rate-limit behavior."""

import asyncio
import io
from datetime import UTC, datetime, timedelta

import pytest

from oxtapus.domain.errors import ResponseValidationError
from oxtapus.progress.events import OperationCompleted, RetryScheduled, TransferAdvanced
from oxtapus.progress.reporter import make_progress_reporter
from oxtapus.progress.terminal import TerminalProgressReporter
from oxtapus.transport.rate_limit import AsyncHostRateLimiter, SyncHostRateLimiter
from oxtapus.transport.response import validate_response_body
from oxtapus.transport.retry import RetryPolicy, parse_retry_after


def test_retry_jitter_and_retry_after_are_deterministic() -> None:
    policy = RetryPolicy(base_delay_seconds=2, max_delay_seconds=10)
    assert policy.delay(2, random_source=lambda: 0.25) == 1.0
    assert policy.delay(1, retry_after="3") == 3.0
    now = datetime(2026, 1, 1, tzinfo=UTC)
    future = (now + timedelta(seconds=4)).strftime("%a, %d %b %Y %H:%M:%S GMT")
    assert parse_retry_after(future, now=now) == 4.0
    assert parse_retry_after("not-a-date") is None


def test_progress_percentage_never_fabricates_unknown_totals() -> None:
    known = TransferAdvanced(
        operation_id="op",
        request_id="req",
        downloaded_bytes=5,
        total_bytes=10,
        bytes_per_second=1,
    )
    complete = TransferAdvanced(
        operation_id="op",
        request_id="req",
        downloaded_bytes=10,
        total_bytes=10,
        bytes_per_second=1,
        complete=True,
    )
    unknown = TransferAdvanced(
        operation_id="op",
        request_id="req",
        downloaded_bytes=5,
        total_bytes=None,
        bytes_per_second=1,
    )
    assert known.percentage == 50
    assert complete.percentage == 100
    assert unknown.percentage is None


def test_callback_and_terminal_reporters() -> None:
    events = []
    reporter = make_progress_reporter(events.append)
    event = RetryScheduled(
        operation_id="op",
        request_id="req",
        endpoint="endpoint",
        attempt=1,
        delay_seconds=0.5,
        reason="temporary",
    )
    reporter.emit(event)
    assert events == [event]
    stream = io.StringIO()
    terminal = TerminalProgressReporter(stream)
    terminal.emit(event)
    terminal.emit(
        OperationCompleted(
            operation_id="op", total=1, success_count=1, failure_count=0, retry_count=1
        )
    )
    assert "retry 1" in stream.getvalue()
    assert "complete" in stream.getvalue()


@pytest.mark.parametrize(
    ("content", "content_type"),
    [(b"", "application/json"), (b"<!doctype html>", "text/html")],
)
def test_response_plausibility_rejects_invalid_bodies(content: bytes, content_type: str) -> None:
    with pytest.raises(ResponseValidationError):
        validate_response_body(content, content_type)


def test_sync_rate_limit_waits_only_as_needed() -> None:
    times = iter([0.0, 0.0, 0.5])
    sleeps: list[float] = []
    limiter = SyncHostRateLimiter(2, clock=lambda: next(times), sleep=sleeps.append)
    limiter.acquire()
    limiter.acquire()
    assert sleeps == [0.5]


async def test_async_rate_limit_is_native() -> None:
    times = iter([0.0, 0.0, 0.5])
    sleeps: list[float] = []

    async def sleep(value: float) -> None:
        sleeps.append(value)
        await asyncio.sleep(0)

    limiter = AsyncHostRateLimiter(2, clock=lambda: next(times), sleep=sleep)
    await limiter.acquire()
    await limiter.acquire()
    assert sleeps == [0.5]
