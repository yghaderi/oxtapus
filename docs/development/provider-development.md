# Provider development

1. Confirm that the source permits the intended access and use.
2. Discover routes from the live first-party application, never from stale code alone.
3. Probe conservatively: multiple instruments/types, empty/malformed identifiers, and
   plausible dates/numbers.
4. Record all endpoint-catalog evidence and a schema fingerprint.
5. Define a strict query model and tolerant additive-field source models.
6. Implement query, extract, and pure transform stages.
7. Map to existing canonical names; propose a canonical version only when semantics change.
8. Add sanitized fixtures, contract tests, quality rules, live canary, docs, and notices.
9. Keep unverified endpoints disabled and document operational limitations.

Do not copy implementation code from reference projects, especially reciprocal-license code.
