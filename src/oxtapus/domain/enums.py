"""Shared domain enumerations."""

from enum import StrEnum


class DataLayer(StrEnum):
    """یکی از لایه‌های مادی خط لولهٔ مهندسی داده."""

    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


class EndpointStatus(StrEnum):
    """وضعیت راستی‌آزمایی یک نقطهٔ پایانی منبع."""

    VERIFIED = "verified"
    EXPERIMENTAL = "experimental"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    REMOVED = "removed"


class ProviderCapability(StrEnum):
    """قابلیت‌های استاندارد فراهم‌کننده که Oxtapus ارائه می‌کند."""

    INSTRUMENT_SEARCH = "instrument_search"
    INSTRUMENT_MASTER = "instrument_master"
    DAILY_PRICES = "daily_prices"
    MARKET_WATCH = "market_watch"
    QUOTE = "quote"
    ORDER_BOOK = "order_book"
    INVESTOR_ACTIVITY = "investor_activity"
    BOARD_MEMBERS = "board_members"
    ASSET_PRICE_HISTORY = "asset_price_history"
    OPTION_CHAIN = "option_chain"
    INDEX_LEVELS = "index_levels"
    MARKET_OVERVIEW = "market_overview"


class FailureMode(StrEnum):
    """رفتار موردنظر هنگام شکست در پردازش گروهی."""

    COLLECT = "collect"
    FAIL_FAST = "fail_fast"


class SchemaPolicy(StrEnum):
    """عملی که هنگام تغییر طرح‌وارهٔ منبع انجام می‌شود."""

    REPORT = "report"
    QUARANTINE = "quarantine"
    ERROR = "error"


class QualitySeverity(StrEnum):
    """شدت اختصاص‌یافته به یک قانون کیفیت داده."""

    ERROR = "error"
    QUARANTINE = "quarantine"
    WARNING = "warning"
    INFORMATIONAL = "informational"


class InstrumentState(StrEnum):
    """وضعیت چرخهٔ عمر یا معاملهٔ یک ابزار مالی."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    RENAMED = "renamed"
    MIGRATED = "migrated"
    SUSPENDED = "suspended"
    UNKNOWN = "unknown"
