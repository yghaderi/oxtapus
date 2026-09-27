"""TGJU endpoint-catalog loading."""

from __future__ import annotations

import tomllib
from importlib.resources import files

from oxtapus.domain.enums import EndpointStatus
from oxtapus.domain.errors import EndpointUnavailableError
from oxtapus.providers.base import EndpointSpec


class TgjuEndpointCatalog:
    """Immutable lookup over packaged TGJU endpoint evidence."""

    def __init__(self, endpoints: dict[str, EndpointSpec], version: str) -> None:
        self._endpoints = endpoints
        self.version = version

    @classmethod
    def load(cls) -> TgjuEndpointCatalog:
        """Load and validate the packaged TOML endpoint catalog."""

        text = (
            files("oxtapus.providers.tgju")
            .joinpath("endpoint_catalog.toml")
            .read_text(encoding="utf-8")
        )
        raw = tomllib.loads(text)
        endpoints = {item["name"]: EndpointSpec.model_validate(item) for item in raw["endpoint"]}
        return cls(endpoints, str(raw["catalog"]["version"]))

    def get(self, name: str) -> EndpointSpec:
        """Return one verified endpoint, failing closed otherwise."""

        spec = self._endpoints[name]
        if spec.status is not EndpointStatus.VERIFIED:
            raise EndpointUnavailableError(
                f"Endpoint {name!r} has status {spec.status.value!r} and is not enabled."
            )
        return spec

    def all(self) -> tuple[EndpointSpec, ...]:
        """Return catalog entries in stable name order."""

        return tuple(self._endpoints[name] for name in sorted(self._endpoints))
