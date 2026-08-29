"""Deterministic source-schema fingerprints and diffs."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


def schema_signature(value: Any) -> Any:
    """Describe JSON structure without retaining source values."""

    if isinstance(value, dict):
        return {str(key): schema_signature(item) for key, item in sorted(value.items())}
    if isinstance(value, list):
        if not value:
            return []
        signatures = {json.dumps(schema_signature(item), sort_keys=True) for item in value[:100]}
        return [json.loads(item) for item in sorted(signatures)]
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    return type(value).__name__


def schema_fingerprint(value: Any) -> str:
    """Return a SHA-256 fingerprint for a JSON-compatible schema."""

    encoded = json.dumps(
        schema_signature(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class SchemaDiff:
    """Structural differences between two source records."""

    added_fields: tuple[str, ...]
    removed_fields: tuple[str, ...]
    changed_types: tuple[str, ...]

    @property
    def changed(self) -> bool:
        """Whether any schema change was found."""

        return bool(self.added_fields or self.removed_fields or self.changed_types)


def schema_diff(expected: Any, observed: Any) -> SchemaDiff:
    """Compare two signatures and report field-level drift."""

    left = _flatten_signature(schema_signature(expected))
    right = _flatten_signature(schema_signature(observed))
    left_keys, right_keys = set(left), set(right)
    return SchemaDiff(
        added_fields=tuple(sorted(right_keys - left_keys)),
        removed_fields=tuple(sorted(left_keys - right_keys)),
        changed_types=tuple(
            sorted(key for key in left_keys & right_keys if left[key] != right[key])
        ),
    )


def _flatten_signature(value: Any, prefix: str = "$") -> dict[str, str]:
    result: dict[str, str] = {}
    if isinstance(value, dict):
        for key, item in value.items():
            result.update(_flatten_signature(item, f"{prefix}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            result.update(_flatten_signature(item, f"{prefix}[{index}]"))
        if not value:
            result[prefix] = "empty_array"
    else:
        result[prefix] = str(value)
    return result
