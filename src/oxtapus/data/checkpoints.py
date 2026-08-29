"""Atomic ingestion checkpoint persistence."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Checkpoint:
    """Resume state for one logical partition."""

    dataset: str
    partition: str
    completed: bool
    checksum: str | None
    updated_at: str


class CheckpointStore:
    """Directory-backed atomic checkpoints."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def save(
        self, dataset: str, partition: str, *, completed: bool, checksum: str | None
    ) -> Checkpoint:
        """Atomically replace one checkpoint."""

        path = self._path(dataset, partition)
        path.parent.mkdir(parents=True, exist_ok=True)
        checkpoint = Checkpoint(
            dataset=dataset,
            partition=partition,
            completed=completed,
            checksum=checksum,
            updated_at=datetime.now(UTC).isoformat(),
        )
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(asdict(checkpoint), sort_keys=True), encoding="utf-8")
        os.replace(temporary, path)
        return checkpoint

    def load(self, dataset: str, partition: str) -> Checkpoint | None:
        """Load a checkpoint when present."""

        path = self._path(dataset, partition)
        if not path.exists():
            return None
        return Checkpoint(**json.loads(path.read_text(encoding="utf-8")))

    def completed(self, dataset: str, partition: str, checksum: str | None = None) -> bool:
        """Return whether a matching partition completed safely."""

        checkpoint = self.load(dataset, partition)
        if checkpoint is None or not checkpoint.completed:
            return False
        return checksum is None or checkpoint.checksum == checksum

    def _path(self, dataset: str, partition: str) -> Path:
        safe = partition.replace("/", "__").replace("=", "-")
        return self.root / dataset / f"{safe}.json"
