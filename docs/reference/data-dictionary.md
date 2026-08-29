# Data dictionary

Core daily-price fields use these meanings:

| Column | Type | Unit | Null behavior |
|---|---|---|---|
| `isin` | string | identifier | preserved when source omits it |
| `symbol` | string | normalized display symbol | required after resolution |
| `tsetmc_instrument_code` | string | identifier | primary-key component |
| `trading_date` | date | Gregorian exchange date | required |
| `open_price` | Int64 | IRR | preserved |
| `high_price` | Int64 | IRR | preserved |
| `low_price` | Int64 | IRR | preserved |
| `close_price` | Int64 | IRR | official closing price; preserved |
| `last_price` | Int64 | IRR | last traded price; preserved |
| `previous_close_price` | Int64 | IRR | preserved |
| `price_change` | Float64 | IRR | signed source difference; fractional anomalies preserved |
| `trade_count` | Int64 | trades | zero is retained, null is not coerced |
| `trade_volume` | Int64 | shares/contracts | zero is retained, null is not coerced |
| `trade_value` | Int64 | IRR | zero is retained, null is not coerced |

Market snapshots add timezone-aware `event_timestamp`, price limits, capitalization, EPS,
and P/E. Option chains add underlying identity, option type, strike, expiration, contract
multiplier, open interest, and best bid/ask. Every calculated field documents its formula in
the canonical transform source; market capitalization is `close_price * shares_outstanding`
and remains null if either input is null.
