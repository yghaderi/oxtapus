"""Progress reporter protocol and factory."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol, runtime_checkable

from oxtapus.progress.events import ProgressEventType


@runtime_checkable
class ProgressReporter(Protocol):
    """Consumes progress events without participating in business logic."""

    def emit(self, event: ProgressEventType) -> None:
        """Consume one event."""


ProgressOption = bool | ProgressReporter | Callable[[ProgressEventType], None] | None


def make_progress_reporter(option: ProgressOption) -> ProgressReporter:
    """Create a reporter from a public API progress option."""

    from oxtapus.progress.callback import CallbackProgressReporter
    from oxtapus.progress.null import NullProgressReporter
    from oxtapus.progress.terminal import TerminalProgressReporter

    if option is True:
        return TerminalProgressReporter()
    if option is False or option is None:
        return NullProgressReporter()
    if isinstance(option, ProgressReporter):
        return option
    return CallbackProgressReporter(option)
