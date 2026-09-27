"""Canonical price schema contracts."""

DAILY_PRICE_COLUMNS = (
    "isin",
    "symbol",
    "tsetmc_instrument_code",
    "trading_date",
    "open_price",
    "high_price",
    "low_price",
    "close_price",
    "last_price",
    "previous_close_price",
    "price_change",
    "trade_count",
    "trade_volume",
    "trade_value",
)

QUOTE_COLUMNS = (
    "tsetmc_instrument_code",
    "symbol",
    "trading_date",
    "event_timestamp",
    "last_event_timestamp",
    "trading_state_code",
    "trading_state",
    "under_supervision",
    "open_price",
    "high_price",
    "low_price",
    "close_price",
    "last_price",
    "previous_close_price",
    "price_change",
    "trade_count",
    "trade_volume",
    "trade_value",
)
