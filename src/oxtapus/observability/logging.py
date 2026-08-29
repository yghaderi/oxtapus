"""Structured logging hooks with sensitive-value redaction."""

from __future__ import annotations

import logging
from collections.abc import Mapping

_SENSITIVE = frozenset({"authorization", "password", "token", "cookie", "api_key"})


def get_logger(name: str = "oxtapus") -> logging.Logger:
    """Return a library logger without configuring global handlers."""

    return logging.getLogger(name)


def redact(fields: Mapping[str, object]) -> dict[str, object]:
    """Redact sensitive structured fields before handing them to a logger."""

    return {
        key: "[REDACTED]" if key.lower() in _SENSITIVE else value for key, value in fields.items()
    }
