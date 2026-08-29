# Observability

Library logging uses the `oxtapus` logger and never configures global handlers. Structured
fields can be passed through the redaction helper. Telemetry is disabled by default; an
application may provide a `TelemetrySink` for counters and durations. Payloads, credentials,
cookies, and proxy secrets must never be telemetry attributes.
