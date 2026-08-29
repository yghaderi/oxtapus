# ADR 0005: Canonical financial naming

## Context
Source abbreviations are unstable and often hide financial meaning or units.

## Decision
Expose versioned English `snake_case` names with explicit price, count, volume, value, date,
timestamp, identifier, currency, and unit semantics.

## Alternatives
Preserving source names and publishing aliases were considered.

## Consequences
Downstream data is provider-independent; version 1.0 requires user code changes.

## Rejected shortcuts
Legacy aliases, silent float coercion, and null-to-zero conversion are rejected.

## Operational implications
Semantic changes require a canonical schema version and data-dictionary update.
