"""Strict JSON envelope parsing."""

from __future__ import annotations

from typing import Any

from oxtapus.domain.errors import ResponseValidationError
from oxtapus.transport.base import RawResponse


def parse_records(response: RawResponse, envelope: str) -> list[dict[str, Any]]:
    """Return an array of object records from the expected envelope."""

    body = response.json()
    if not isinstance(body, dict) or envelope not in body:
        raise ResponseValidationError(
            f"Endpoint {response.endpoint!r} did not return envelope {envelope!r}."
        )
    records = body[envelope]
    if not isinstance(records, list) or any(not isinstance(item, dict) for item in records):
        raise ResponseValidationError(f"Envelope {envelope!r} must be an array of objects.")
    return records


def parse_nullable_records(response: RawResponse, envelope: str) -> list[dict[str, Any]]:
    """Return object records while treating a present null envelope as an empty result."""

    body = response.json()
    if not isinstance(body, dict) or envelope not in body:
        raise ResponseValidationError(
            f"Endpoint {response.endpoint!r} did not return envelope {envelope!r}."
        )
    records = body[envelope]
    if records is None:
        return []
    if not isinstance(records, list) or any(not isinstance(item, dict) for item in records):
        raise ResponseValidationError(f"Envelope {envelope!r} must be null or an array of objects.")
    return records


def parse_object(response: RawResponse, envelope: str) -> dict[str, Any]:
    """Return one object from the expected envelope."""

    body = response.json()
    if not isinstance(body, dict) or envelope not in body:
        raise ResponseValidationError(
            f"Endpoint {response.endpoint!r} did not return envelope {envelope!r}."
        )
    record = body[envelope]
    if not isinstance(record, dict):
        raise ResponseValidationError(f"Envelope {envelope!r} must be an object.")
    return record
