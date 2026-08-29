"""Versioned data-catalog loader."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from importlib.resources import files
from typing import Any, cast

from oxtapus.domain.enums import DataLayer


@dataclass(frozen=True, slots=True)
class DatasetSpec:
    """One versioned canonical dataset contract."""

    name: str
    description: str
    layer: DataLayer
    owner: str
    provider_capability: str
    schema_version: str
    primary_key: tuple[str, ...]
    partition_columns: tuple[str, ...]
    sort_columns: tuple[str, ...]
    update_cadence: str
    freshness_expectation: str
    currency: str
    unit: str
    duplicate_policy: str
    null_policy: str
    quality_rules: tuple[str, ...]
    storage_format: str
    retention_policy: str
    lineage: str


class DataCatalog:
    """Read-only lookup for packaged dataset contracts."""

    def __init__(self, specs: dict[str, DatasetSpec], version: str) -> None:
        self._specs = specs
        self.version = version

    @classmethod
    def load(cls) -> DataCatalog:
        """Load the packaged TOML catalog."""

        raw = tomllib.loads(
            files("oxtapus.data").joinpath("data_catalog.toml").read_text(encoding="utf-8")
        )
        specs: dict[str, DatasetSpec] = {}
        for untyped in raw["dataset"]:
            item = cast(dict[str, Any], untyped)
            spec = DatasetSpec(
                name=str(item["name"]),
                description=str(item["description"]),
                layer=DataLayer(str(item["layer"])),
                owner=str(item["owner"]),
                provider_capability=str(item["provider_capability"]),
                schema_version=str(item["schema_version"]),
                primary_key=_strings(item["primary_key"]),
                partition_columns=_strings(item["partition_columns"]),
                sort_columns=_strings(item["sort_columns"]),
                update_cadence=str(item["update_cadence"]),
                freshness_expectation=str(item["freshness_expectation"]),
                currency=str(item["currency"]),
                unit=str(item["unit"]),
                duplicate_policy=str(item["duplicate_policy"]),
                null_policy=str(item["null_policy"]),
                quality_rules=_strings(item["quality_rules"]),
                storage_format=str(item["storage_format"]),
                retention_policy=str(item["retention_policy"]),
                lineage=str(item["lineage"]),
            )
            specs[spec.name] = spec
        return cls(specs, str(raw["catalog"]["version"]))

    def get(self, name: str) -> DatasetSpec:
        """Return one dataset spec."""

        return self._specs[name]

    def list(self) -> tuple[DatasetSpec, ...]:
        """Return all specs in stable name order."""

        return tuple(self._specs[name] for name in sorted(self._specs))


def _strings(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in cast(list[Any], value))
