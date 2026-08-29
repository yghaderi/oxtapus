"""Typed progress event stream."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class ProgressEvent:
    """Base progress event."""

    operation_id: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True, kw_only=True)
class OperationStarted(ProgressEvent):
    """A batch operation has started."""

    capability: str
    total_items: int | None
    resumed_items: int = 0


@dataclass(frozen=True, slots=True, kw_only=True)
class TransferStarted(ProgressEvent):
    """A response body transfer has started."""

    request_id: str
    endpoint: str
    total_bytes: int | None


@dataclass(frozen=True, slots=True, kw_only=True)
class TransferAdvanced(ProgressEvent):
    """A response body yielded more bytes."""

    request_id: str
    downloaded_bytes: int
    total_bytes: int | None
    bytes_per_second: float
    complete: bool = False

    @property
    def percentage(self) -> float | None:
        """Return a real transfer percentage, or ``None`` when indeterminate."""

        if self.total_bytes is None or self.total_bytes <= 0:
            return None
        value = self.downloaded_bytes / self.total_bytes * 100
        return 100.0 if self.complete else min(value, 99.999999)


@dataclass(frozen=True, slots=True, kw_only=True)
class ItemStarted(ProgressEvent):
    """A batch work item has started."""

    item: str
    completed: int
    total: int


@dataclass(frozen=True, slots=True, kw_only=True)
class RetryScheduled(ProgressEvent):
    """One request will be retried after a delay."""

    request_id: str
    endpoint: str
    attempt: int
    delay_seconds: float
    reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ItemCompleted(ProgressEvent):
    """A batch work item completed successfully."""

    item: str
    completed: int
    total: int
    success_count: int
    failure_count: int
    retry_count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class ItemFailed(ProgressEvent):
    """A batch work item failed."""

    item: str
    completed: int
    total: int
    success_count: int
    failure_count: int
    retry_count: int
    error: str


@dataclass(frozen=True, slots=True, kw_only=True)
class OperationCompleted(ProgressEvent):
    """A batch operation finished."""

    total: int
    success_count: int
    failure_count: int
    retry_count: int
    skipped_count: int = 0


@dataclass(frozen=True, slots=True, kw_only=True)
class OperationCancelled(ProgressEvent):
    """A batch operation was cancelled."""

    completed: int
    total: int


ProgressEventType = (
    OperationStarted
    | TransferStarted
    | TransferAdvanced
    | ItemStarted
    | RetryScheduled
    | ItemCompleted
    | ItemFailed
    | OperationCompleted
    | OperationCancelled
)
