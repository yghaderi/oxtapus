"""Tolerant TGJU source-envelope models."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TgjuHistoryEnvelope(BaseModel):
    """DataTables-shaped historical price response."""

    model_config = ConfigDict(extra="allow")

    data: list[list[Any]]
    draw: int | None = None
    recordsFiltered: int | None = Field(default=None, ge=0)
    recordsTotal: int | None = Field(default=None, ge=0)

    def unknown_fields(self) -> tuple[str, ...]:
        """Return additive root fields for schema-drift reporting."""

        return tuple(sorted((self.model_extra or {}).keys()))
