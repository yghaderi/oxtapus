# Troubleshooting

**No rows for a symbol:** call `instrument_search`, normalize the exact symbol, and inspect
advanced `failures`. Oxtapus does not choose fuzzy candidates.

**Temporary status errors:** inspect retry events and `retry_count`. Increase bounded timeout
or retry budgets carefully; do not disable rate limits.

**Schema validation error:** save the sanitized response as Bronze, compare fingerprints, and
run the provider doctor. Do not weaken required fields before verifying source semantics.

**Arrow, Pandas, or DuckDB import error:** install the corresponding optional extra.

**Async notebook issue:** use `AsyncClient` with top-level `await`; do not wrap it in an event
loop runner.
