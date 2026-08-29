"""Per-request retry policy and Retry-After parsing."""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Bounded exponential backoff with full jitter."""

    max_attempts: int = 4
    base_delay_seconds: float = 0.5
    max_delay_seconds: float = 15.0
    max_total_delay_seconds: float = 45.0
    retry_status_codes: frozenset[int] = frozenset({408, 425, 429, 500, 502, 503, 504})

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least one")
        if (
            min(
                self.base_delay_seconds,
                self.max_delay_seconds,
                self.max_total_delay_seconds,
            )
            < 0
        ):
            raise ValueError("retry delays cannot be negative")

    def delay(
        self,
        attempt: int,
        *,
        retry_after: str | None = None,
        now: datetime | None = None,
        random_source: Callable[[], float] = random.random,
    ) -> float:
        """Calculate the delay before the next attempt."""

        parsed = parse_retry_after(retry_after, now=now)
        if parsed is not None:
            return min(parsed, self.max_delay_seconds)
        cap = min(self.base_delay_seconds * 2 ** max(0, attempt - 1), self.max_delay_seconds)
        return cap * min(max(random_source(), 0.0), 1.0)


def parse_retry_after(value: str | None, *, now: datetime | None = None) -> float | None:
    """Parse Retry-After seconds or an HTTP date."""

    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        pass
    try:
        target = parsedate_to_datetime(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if target.tzinfo is None:
        target = target.replace(tzinfo=UTC)
    current = now or datetime.now(UTC)
    return max(0.0, (target - current).total_seconds())
