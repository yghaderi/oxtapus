"""Minimal terminal and notebook progress rendering."""

from __future__ import annotations

import sys
from typing import TextIO

from oxtapus.progress.events import (
    ItemCompleted,
    ItemFailed,
    OperationCompleted,
    OperationStarted,
    ProgressEventType,
    RetryScheduled,
    TransferAdvanced,
)


class TerminalProgressReporter:
    """Render compact, line-oriented progress to a text stream."""

    def __init__(self, stream: TextIO | None = None) -> None:
        self._stream = stream or sys.stderr

    def emit(self, event: ProgressEventType) -> None:
        """Render events that are meaningful to a human."""

        line: str | None = None
        if isinstance(event, OperationStarted):
            total = "?" if event.total_items is None else str(event.total_items)
            line = f"{event.capability}: 0/{total} items"
        elif isinstance(event, TransferAdvanced) and event.complete:
            if event.percentage is None:
                line = f"downloaded {event.downloaded_bytes:,} bytes"
            else:
                line = f"downloaded {event.downloaded_bytes:,} bytes (100%)"
        elif isinstance(event, RetryScheduled):
            line = f"retry {event.attempt} in {event.delay_seconds:.2f}s: {event.reason}"
        elif isinstance(event, (ItemCompleted, ItemFailed)):
            line = (
                f"{event.completed}/{event.total} items; "
                f"ok={event.success_count} failed={event.failure_count} retries={event.retry_count}"
            )
        elif isinstance(event, OperationCompleted):
            line = (
                f"complete: ok={event.success_count} failed={event.failure_count} "
                f"retries={event.retry_count} skipped={event.skipped_count}"
            )
        if line is not None:
            self._stream.write(line + "\n")
            self._stream.flush()
