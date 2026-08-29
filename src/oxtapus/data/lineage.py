"""Serializable dataset lineage."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any

from oxtapus.domain.enums import DataLayer


@dataclass(frozen=True, slots=True)
class LineageNode:
    """One immutable transformation node."""

    dataset: str
    layer: DataLayer
    schema_version: str
    operation: str
    inputs: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class Lineage:
    """Ordered lineage nodes for one result."""

    run_id: str
    nodes: tuple[LineageNode, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""

        return {"run_id": self.run_id, "nodes": [asdict(node) for node in self.nodes]}
