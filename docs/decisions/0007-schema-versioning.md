# ADR 0007: Schema versioning

## Context
Upstream additive, missing, or type-changing fields have different compatibility risks.

## Decision
Version source and canonical schemas separately; fingerprint raw structure, report additive
fields, and fail required-field/type violations under configured policy.

## Alternatives
Ignoring unknown fields and rejecting every addition were considered.

## Consequences
Compatible drift is visible without needless outage; incompatible drift is explicit.

## Rejected shortcuts
Silent field loss and schema inference as the only contract are rejected.

## Operational implications
Canaries compare fingerprints and maintainers update fixtures and catalog evidence.
