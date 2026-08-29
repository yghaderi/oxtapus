"""Callback-backed progress reporter."""

from collections.abc import Callable

from oxtapus.progress.events import ProgressEventType


class CallbackProgressReporter:
    """Forward progress events to an application callback."""

    def __init__(self, callback: Callable[[ProgressEventType], None]) -> None:
        self._callback = callback

    def emit(self, event: ProgressEventType) -> None:
        """Forward one event."""

        self._callback(event)
