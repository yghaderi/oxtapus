# ADR 0008: Hard public API replacement

## Context
The 0.x surface encoded provider routes, mutable modes, source columns, and inconsistent errors.

## Decision
Version 1.0 replaces it entirely with a small capability-oriented API and no compatibility tree.

## Alternatives
A deprecation period, aliases, and adapters were considered.

## Consequences
Existing callers must rewrite imports and column use; the new design has no legacy constraints.

## Rejected shortcuts
Deprecated wrappers, old exception emulation, and duplicated column aliases are rejected.

## Operational implications
The major version and changelog communicate the break; wheel audits enforce the small surface.
