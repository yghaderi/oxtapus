# Oxtapus architecture rules

Before a human engineer or coding agent modifies a bounded context, they must read
the root architecture rules and the nearest local bounded-context rules.

Oxtapus 1.x is a deliberate replacement of the 0.x package. Never add compatibility
wrappers, deprecated aliases, provider facades, or legacy column names.

## Dependency boundaries

- Domain code is provider-, transport-, tabular-engine-, and storage-independent.
- Transport code knows HTTP and resilience, never financial schemas.
- Provider extraction performs remote access and never persistence.
- Provider transformation is deterministic and never performs remote access.
- Gold transformations consume canonical data only and never perform remote access.
- Public API and CLI code call application services.
- Progress, observability, quality, and persistence remain separate concerns.

## Engineering rules

- Public data columns use canonical English `snake_case` names.
- Identifiers are strings. Counts, volumes, and integral prices remain integers.
- Missing or malformed values are never converted to zero.
- Every default endpoint must be live-verified and listed in the endpoint catalog.
- Fixtures, not live availability, drive normal CI.
- Provider payload additions must be surfaced as schema drift.
- Library internals use structured logging and progress events, never `print()`.
- Keep synchronous and asynchronous implementations native and feature-equivalent.
