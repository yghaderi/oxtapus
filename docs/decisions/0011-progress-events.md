# ADR 0011: Progress event architecture

## Context
Network bytes, batch completion, retries, failures, cancellation, terminals, and notebooks need
one truthful model without coupling rendering to business logic.

## Decision
Emit typed immutable events through a reporter protocol with callback, terminal, and null adapters.

## Alternatives
Printing in transport and callback-only byte counters were considered.

## Consequences
Applications can render or record progress consistently across sync and async paths.

## Rejected shortcuts
Invented percentages for unknown lengths and retry-silent progress are rejected.

## Operational implications
Known transfers reach exactly 100%; batches count completed items and cancellation is explicit.
