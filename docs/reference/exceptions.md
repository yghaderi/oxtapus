# Exceptions

All package errors derive from `OxtapusError`. Typed branches cover configuration,
unsupported capabilities, unavailable endpoints, transport/status/retry exhaustion,
response/schema/schema-drift validation, data quality, storage, missing or ambiguous
instruments, invalid identifiers, and partial batch failure. `RetryExhaustedError.original`
preserves the final cause; ambiguity errors preserve candidate records.
