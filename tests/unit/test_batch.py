"""Batch success, failure, callback, and cancellation contracts."""

import asyncio

import pytest

from oxtapus.application.batch import run_batch, run_batch_async
from oxtapus.domain.enums import FailureMode
from oxtapus.progress.events import OperationCancelled, ProgressEventType
from oxtapus.progress.reporter import make_progress_reporter


def test_sync_batch_collects_item_failures() -> None:
    events: list[ProgressEventType] = []

    def worker(item: str) -> str:
        if item == "bad":
            raise ValueError("isolated")
        return item.upper()

    outcome = run_batch(
        ["ok", "bad"],
        worker,
        capability="test",
        operation_id="operation",
        reporter=make_progress_reporter(events.append),
        concurrency=2,
        failure_mode=FailureMode.COLLECT,
    )
    assert outcome.values == ("OK",)
    assert len(outcome.failures) == 1
    assert events[-1].success_count == 1


async def test_async_batch_collects_item_failures() -> None:
    async def worker(item: str) -> str:
        await asyncio.sleep(0)
        if item == "bad":
            raise ValueError("isolated")
        return item.upper()

    outcome = await run_batch_async(
        ["ok", "bad"],
        worker,
        capability="test",
        operation_id="operation",
        reporter=make_progress_reporter(False),
        concurrency=2,
        failure_mode=FailureMode.COLLECT,
    )
    assert outcome.values == ("OK",)
    assert len(outcome.failures) == 1


async def test_async_batch_reports_cancellation() -> None:
    events: list[ProgressEventType] = []

    async def worker(item: str) -> str:
        await asyncio.Event().wait()
        return item

    task = asyncio.create_task(
        run_batch_async(
            ["wait"],
            worker,
            capability="test",
            operation_id="operation",
            reporter=make_progress_reporter(events.append),
            concurrency=1,
            failure_mode=FailureMode.COLLECT,
        )
    )
    await asyncio.sleep(0)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert any(isinstance(event, OperationCancelled) for event in events)
