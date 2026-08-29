"""Optional telemetry protocol; disabled by default."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol


class TelemetrySink(Protocol):
    """Application-owned metrics boundary."""

    def counter(self, name: str, value: int, attributes: Mapping[str, str]) -> None:
        """Record one counter delta."""

    def duration(self, name: str, seconds: float, attributes: Mapping[str, str]) -> None:
        """Record one duration observation."""


class NullTelemetry:
    """No-op default preserving zero telemetry side effects."""

    def counter(self, name: str, value: int, attributes: Mapping[str, str]) -> None:
        pass

    def duration(self, name: str, seconds: float, attributes: Mapping[str, str]) -> None:
        pass
