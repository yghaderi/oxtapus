# ADR 0010: Endpoint verification policy

## Context
An endpoint present in old code or a third-party project is not proof of current correctness.

## Decision
Fail closed until conservative live probes record route, parameters, envelope, identifiers,
types, negative cases, plausibility, headers, size, timestamp, fingerprint, status, and limits.

## Alternatives
Trusting old routes, automatic fallback, and undocumented discovery were considered.

## Consequences
The enabled capability set can be smaller than the discovered route inventory.

## Rejected shortcuts
Status-only health checks and single-symbol validation are rejected.

## Operational implications
Scheduled opt-in canaries surface drift; ordinary CI remains offline.
