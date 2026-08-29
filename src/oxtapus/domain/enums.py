"""Shared domain enumerations."""

from enum import StrEnum


class DataLayer(StrEnum):
    """A material data-engineering layer."""

    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


class EndpointStatus(StrEnum):
    """Verification state of an upstream endpoint."""

    VERIFIED = "verified"
    EXPERIMENTAL = "experimental"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    REMOVED = "removed"


class ProviderCapability(StrEnum):
    """Canonical provider capabilities exposed by Oxtapus."""

    INSTRUMENT_SEARCH = "instrument_search"
    INSTRUMENT_MASTER = "instrument_master"
    DAILY_PRICES = "daily_prices"
    MARKET_WATCH = "market_watch"
    OPTION_CHAIN = "option_chain"
    INDEX_LEVELS = "index_levels"
    MARKET_OVERVIEW = "market_overview"


class FailureMode(StrEnum):
    """Batch failure behavior."""

    COLLECT = "collect"
    FAIL_FAST = "fail_fast"


class SchemaPolicy(StrEnum):
    """Action taken when a source schema changes."""

    REPORT = "report"
    QUARANTINE = "quarantine"
    ERROR = "error"


class QualitySeverity(StrEnum):
    """Severity assigned to a data-quality rule."""

    ERROR = "error"
    QUARANTINE = "quarantine"
    WARNING = "warning"
    INFORMATIONAL = "informational"


class InstrumentState(StrEnum):
    """Lifecycle or trading state of an instrument."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    RENAMED = "renamed"
    MIGRATED = "migrated"
    SUSPENDED = "suspended"
    UNKNOWN = "unknown"
