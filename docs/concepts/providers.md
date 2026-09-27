# Providers

A provider advertises capabilities, not a website-shaped public class. Each fetcher has three
stages: validate/normalize the query, extract a raw response, and transform it to canonical
data. Endpoint specifications are catalog-owned and fail closed unless live evidence marks
them verified.

The verified TSETMC website provider serves securities data. A separately catalogued TGJU
provider serves the explicitly enabled currency and gold-coin histories. Unverified sources
and arbitrary upstream identifiers are not kept as fallbacks or placeholders.
