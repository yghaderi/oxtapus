# TSETMC provider rules

Read the root `AGENTS.md` before changing this bounded context.

- The endpoint catalog is evidence, not a wish list. Default code may use only verified entries.
- Add or change a route only after conservative live probing and sanitized contract fixtures.
- Source models retain source field names and allow additive fields while reporting them.
- Fetcher stages are strict: query normalization, source extraction, canonical transformation.
- Extraction never persists. Transformation never performs remote access.
- Required headers are sent honestly. Never evade throttling or access controls.
- Keep fixture bodies minimal and remove cookies, request identifiers, and tracking headers.
