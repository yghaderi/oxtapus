# ADR 0001: HTTPX2 transport boundary

## Context
The SDK needs pooling, streaming, timeouts, injection, sync/async parity, and testable retries.

## Decision
All remote access crosses provider-neutral HTTPX2 sync or async transports.

## Alternatives
Direct calls in fetchers and multiple HTTP libraries were considered.

## Consequences
Providers construct requests but never own clients or retry loops.

## Rejected shortcuts
Per-call clients, implicit global clients, and mixed HTTP dependencies are rejected.

## Operational implications
Applications tune four timeouts, pools, TLS, proxy, HTTP/2, rate, hooks, and bounded retries.
