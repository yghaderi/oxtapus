# Providers

A provider advertises capabilities, not a website-shaped public class. Each fetcher has three
stages: validate/normalize the query, extract a raw response, and transform it to canonical
data. Endpoint specifications are catalog-owned and fail closed unless live evidence marks
them verified.

Only the official TSETMC website provider is enabled in 1.0. Unverified sources are not kept as
fallbacks or placeholders.
