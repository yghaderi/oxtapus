"""Typed configuration with safe network defaults."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from oxtapus.domain.enums import DataLayer, FailureMode, SchemaPolicy

_ALLOWED_PROVIDER_HOSTS = frozenset({"https://api.tgju.org", "https://cdn.tsetmc.com"})


class Settings(BaseSettings):
    """تنظیمات اجرا با اولویت آرگومان، متغیر محیطی و سپس مقدار پیش‌فرض."""

    model_config = SettingsConfigDict(
        env_prefix="OXTAPUS_",
        env_nested_delimiter="__",
        extra="forbid",
        frozen=True,
    )

    provider: str = "tsetmc"
    endpoint_priority: tuple[str, ...] = ("tsetmc",)
    base_urls: tuple[str, ...] = ("https://cdn.tsetmc.com", "https://api.tgju.org")
    user_agent: str = "Oxtapus/1.1 (+https://github.com/yghaderi/oxtapus)"
    http2: bool = False
    verify_tls: bool = True
    proxy: str | None = None
    connect_timeout: float = Field(default=5.0, gt=0)
    read_timeout: float = Field(default=30.0, gt=0)
    write_timeout: float = Field(default=10.0, gt=0)
    pool_timeout: float = Field(default=5.0, gt=0)
    max_connections: int = Field(default=10, ge=1)
    max_keepalive_connections: int = Field(default=5, ge=0)
    concurrency: int = Field(default=4, ge=1, le=32)
    requests_per_second: float = Field(default=2.0, gt=0, le=20)
    retry_max_attempts: int = Field(default=4, ge=1, le=10)
    retry_base_delay: float = Field(default=0.5, ge=0)
    retry_max_delay: float = Field(default=15.0, ge=0)
    retry_total_delay_budget: float = Field(default=30.0, ge=0)
    progress: bool = False
    cache_directory: Path = Path(".oxtapus/cache")
    data_directory: Path = Path(".oxtapus/data")
    storage_backend: str = "memory"
    persisted_data_layers: tuple[DataLayer, ...] = ()
    schema_policy: SchemaPolicy = SchemaPolicy.REPORT
    quality_policy: str = "report"
    failure_mode: FailureMode = FailureMode.COLLECT
    freshness_seconds: int = Field(default=300, ge=0)
    logging_enabled: bool = False
    telemetry_enabled: bool = False

    @field_validator("provider")
    @classmethod
    def verified_provider(cls, value: str) -> str:
        if value != "tsetmc":
            raise ValueError("Only the verified 'tsetmc' provider is enabled.")
        return value

    @field_validator("base_urls")
    @classmethod
    def trusted_hosts_only(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(item.rstrip("/") for item in value)
        untrusted = set(normalized) - _ALLOWED_PROVIDER_HOSTS
        if untrusted:
            raise ValueError(f"Untrusted provider hosts are not allowed: {sorted(untrusted)}")
        return normalized

    @field_validator("endpoint_priority")
    @classmethod
    def known_endpoint_priority(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if not value or set(value) != {"tsetmc"}:
            raise ValueError("endpoint_priority must contain only 'tsetmc'.")
        return value

    @field_validator("storage_backend")
    @classmethod
    def known_storage(cls, value: str) -> str:
        if value not in {"memory", "parquet", "duckdb"}:
            raise ValueError("storage_backend must be memory, parquet, or duckdb.")
        return value

    @field_validator("quality_policy")
    @classmethod
    def known_quality_policy(cls, value: str) -> str:
        if value not in {"error", "quarantine", "report"}:
            raise ValueError("quality_policy must be error, quarantine, or report.")
        return value
