"""Bounded native sync and async batch execution."""

from __future__ import annotations

import asyncio
import threading
from collections.abc import Awaitable, Callable, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Generic, TypeVar

from oxtapus.domain.enums import FailureMode
from oxtapus.progress.events import (
    ItemCompleted,
    ItemFailed,
    ItemStarted,
    OperationCancelled,
    OperationCompleted,
    OperationStarted,
)
from oxtapus.progress.reporter import ProgressReporter
from oxtapus.providers.base import FetchFailure

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class BatchOutcome(Generic[T]):
    """Successful values and item-scoped failures in caller-independent order."""

    values: tuple[T, ...]
    failures: tuple[FetchFailure, ...]


def run_batch(
    items: Sequence[str],
    worker: Callable[[str], T],
    *,
    capability: str,
    operation_id: str,
    reporter: ProgressReporter,
    concurrency: int,
    failure_mode: FailureMode,
) -> BatchOutcome[T]:
    """Execute work with bounded threads and isolate retries inside each item."""

    reporter.emit(
        OperationStarted(
            operation_id=operation_id,
            capability=capability,
            total_items=len(items),
        )
    )
    values: list[T] = []
    failures: list[FetchFailure] = []
    lock = threading.Lock()
    completed = 0
    with ThreadPoolExecutor(max_workers=max(1, concurrency), thread_name_prefix="oxtapus") as pool:
        futures = {}
        for item in items:
            reporter.emit(
                ItemStarted(
                    operation_id=operation_id,
                    item=item,
                    completed=completed,
                    total=len(items),
                )
            )
            futures[pool.submit(worker, item)] = item
        for future in as_completed(futures):
            item = futures[future]
            with lock:
                completed += 1
            try:
                value = future.result()
            except Exception as exc:
                failure = FetchFailure(item, type(exc).__name__, str(exc))
                failures.append(failure)
                reporter.emit(
                    ItemFailed(
                        operation_id=operation_id,
                        item=item,
                        completed=completed,
                        total=len(items),
                        success_count=len(values),
                        failure_count=len(failures),
                        retry_count=0,
                        error=str(exc),
                    )
                )
                if failure_mode is FailureMode.FAIL_FAST:
                    for sibling in futures:
                        sibling.cancel()
                    raise
            else:
                values.append(value)
                reporter.emit(
                    ItemCompleted(
                        operation_id=operation_id,
                        item=item,
                        completed=completed,
                        total=len(items),
                        success_count=len(values),
                        failure_count=len(failures),
                        retry_count=_retry_count(value),
                    )
                )
    reporter.emit(
        OperationCompleted(
            operation_id=operation_id,
            total=len(items),
            success_count=len(values),
            failure_count=len(failures),
            retry_count=sum(_retry_count(item) for item in values),
        )
    )
    return BatchOutcome(tuple(values), tuple(failures))


async def run_batch_async(
    items: Sequence[str],
    worker: Callable[[str], Awaitable[T]],
    *,
    capability: str,
    operation_id: str,
    reporter: ProgressReporter,
    concurrency: int,
    failure_mode: FailureMode,
) -> BatchOutcome[T]:
    """Execute native async work with a semaphore and cancellation propagation."""

    reporter.emit(
        OperationStarted(
            operation_id=operation_id,
            capability=capability,
            total_items=len(items),
        )
    )
    semaphore = asyncio.Semaphore(max(1, concurrency))
    completed = 0
    successes = 0
    failures: list[FetchFailure] = []

    async def invoke(item: str) -> T | FetchFailure:
        nonlocal completed, successes
        reporter.emit(
            ItemStarted(
                operation_id=operation_id,
                item=item,
                completed=completed,
                total=len(items),
            )
        )
        try:
            async with semaphore:
                value = await worker(item)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            completed += 1
            failure = FetchFailure(item, type(exc).__name__, str(exc))
            failures.append(failure)
            reporter.emit(
                ItemFailed(
                    operation_id=operation_id,
                    item=item,
                    completed=completed,
                    total=len(items),
                    success_count=successes,
                    failure_count=len(failures),
                    retry_count=0,
                    error=str(exc),
                )
            )
            if failure_mode is FailureMode.FAIL_FAST:
                raise
            return failure
        completed += 1
        successes += 1
        reporter.emit(
            ItemCompleted(
                operation_id=operation_id,
                item=item,
                completed=completed,
                total=len(items),
                success_count=successes,
                failure_count=len(failures),
                retry_count=_retry_count(value),
            )
        )
        return value

    tasks = [asyncio.create_task(invoke(item)) for item in items]
    try:
        outcomes = await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        for task in tasks:
            task.cancel()
        reporter.emit(
            OperationCancelled(
                operation_id=operation_id,
                completed=completed,
                total=len(items),
            )
        )
        raise
    values = tuple(item for item in outcomes if not isinstance(item, FetchFailure))
    reporter.emit(
        OperationCompleted(
            operation_id=operation_id,
            total=len(items),
            success_count=len(values),
            failure_count=len(failures),
            retry_count=sum(_retry_count(item) for item in values),
        )
    )
    return BatchOutcome(values, tuple(failures))


def _retry_count(value: object) -> int:
    response = getattr(value, "response", None)
    return int(getattr(response, "retry_count", 0))
