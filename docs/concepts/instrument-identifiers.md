# Instrument identifiers

High-level methods accept Persian symbols, ISINs, official instrument codes, and provider
instrument IDs. Arabic Yeh/Kaf, zero-width characters, non-breaking spaces, and repeated
whitespace are normalized before matching.

Resolution never picks an arbitrary fuzzy candidate. Exact matches are enriched from the
instrument endpoint; missing and ambiguous identifiers raise typed errors, and ambiguity
errors retain candidate records.
