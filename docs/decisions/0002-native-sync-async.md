# ADR 0002: Native sync and async separation

## Context
Notebooks and services need both modes without event-loop ownership failures.

## Decision
Maintain native sync and async transports, services, resolvers, clients, limiters, and backoff.

## Alternatives
Running async from sync, running sync in executors, and a mutable mode flag were considered.

## Consequences
The two paths have matching capabilities but explicit lifecycles.

## Rejected shortcuts
Loop runners, loop patching, and hidden thread adaptation are rejected.

## Operational implications
Users select `Client` or `AsyncClient`; injected resources remain caller-owned.
