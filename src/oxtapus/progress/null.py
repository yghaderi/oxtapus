"""No-op progress reporter."""

from oxtapus.progress.events import ProgressEventType


class NullProgressReporter:
    """Discard all progress events."""

    def emit(self, event: ProgressEventType) -> None:
        """Discard one event."""
