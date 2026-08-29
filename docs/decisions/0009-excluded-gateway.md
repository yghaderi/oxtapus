# ADR 0009: Exclude a retired gateway

## Context
Historical code referenced `webgw.tse.ir`, but current first-party website assets use a
different verified data path and the retired gateway is not an acceptable dependency.

## Decision
Exclude the gateway from runtime, tests, catalogs, examples, configuration, fallbacks, health
checks, and future placeholders.

## Alternatives
Primary, fallback, experimental, and health-check use were considered.

## Consequences
No capability depends on the retired host; current source discovery is independently evidenced.

## Rejected shortcuts
Keeping dormant routes or configurable escape hatches is rejected.

## Operational implications
Repository audits allow this hostname only in this decision record.
