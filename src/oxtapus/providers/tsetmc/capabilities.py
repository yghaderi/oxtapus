"""Endpoint-catalog loading and verified capability discovery."""

from __future__ import annotations

import tomllib
from importlib.resources import files

from oxtapus.domain.enums import EndpointStatus, ProviderCapability
from oxtapus.domain.errors import EndpointUnavailableError
from oxtapus.providers.base import EndpointSpec


class EndpointCatalog:
    """Immutable lookup over packaged endpoint evidence."""

    def __init__(self, endpoints: dict[str, EndpointSpec], version: str) -> None:
        self._endpoints = endpoints
        self.version = version

    @classmethod
    def load(cls) -> EndpointCatalog:
        """Load and validate the packaged TOML endpoint catalog."""

        text = (
            files("oxtapus.providers.tsetmc")
            .joinpath("endpoint_catalog.toml")
            .read_text(encoding="utf-8")
        )
        raw = tomllib.loads(text)
        endpoints = {item["name"]: EndpointSpec.model_validate(item) for item in raw["endpoint"]}
        return cls(endpoints, str(raw["catalog"]["version"]))

    def get(self, name: str, *, experimental: bool = False) -> EndpointSpec:
        """Return an enabled endpoint, failing closed for unverified entries."""

        spec = self._endpoints[name]
        allowed = spec.status is EndpointStatus.VERIFIED or (
            experimental and spec.status is EndpointStatus.EXPERIMENTAL
        )
        if not allowed:
            raise EndpointUnavailableError(
                f"Endpoint {name!r} has status {spec.status.value!r} and is not enabled."
            )
        return spec

    def all(self) -> tuple[EndpointSpec, ...]:
        """Return every catalog entry in stable name order."""

        return tuple(self._endpoints[name] for name in sorted(self._endpoints))

    def verified_capabilities(self) -> tuple[ProviderCapability, ...]:
        """Return capabilities backed by at least one verified endpoint."""

        values = {
            endpoint.capability
            for endpoint in self._endpoints.values()
            if endpoint.status is EndpointStatus.VERIFIED
        }
        return tuple(sorted(values, key=str))
