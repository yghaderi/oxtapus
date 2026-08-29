"""Conservative process-local host rate limiting."""

from __future__ import annotations

import asyncio
import threading
import time
from collections.abc import Awaitable, Callable


class SyncHostRateLimiter:
    """Serialize minimum request spacing across threads."""

    def __init__(
        self,
        requests_per_second: float,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._interval = 0.0 if requests_per_second <= 0 else 1.0 / requests_per_second
        self._clock = clock
        self._sleep = sleep
        self._next_allowed = 0.0
        self._lock = threading.Lock()

    def acquire(self) -> None:
        """Wait until one request is allowed."""

        if self._interval <= 0:
            return
        with self._lock:
            now = self._clock()
            delay = max(0.0, self._next_allowed - now)
            if delay:
                self._sleep(delay)
                now = self._clock()
            self._next_allowed = max(now, self._next_allowed) + self._interval


class AsyncHostRateLimiter:
    """Serialize minimum request spacing across async tasks."""

    def __init__(
        self,
        requests_per_second: float,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self._interval = 0.0 if requests_per_second <= 0 else 1.0 / requests_per_second
        self._clock = clock
        self._sleep = sleep
        self._next_allowed = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Wait until one request is allowed."""

        if self._interval <= 0:
            return
        async with self._lock:
            now = self._clock()
            delay = max(0.0, self._next_allowed - now)
            if delay:
                await self._sleep(delay)
                now = self._clock()
            self._next_allowed = max(now, self._next_allowed) + self._interval
