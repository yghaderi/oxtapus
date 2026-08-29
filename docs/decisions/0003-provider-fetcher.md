# ADR 0003: Provider and fetcher model

## Context
Website-shaped facades couple public APIs to unstable source routes.

## Decision
Providers advertise capabilities; typed fetchers separate query normalization, extraction,
and pure transformation.

## Alternatives
One large provider class and dynamically shaped dictionary calls were considered.

## Consequences
Source changes remain within adapters and capability discovery is explicit.

## Rejected shortcuts
Fallback-by-exception and implicit endpoint selection are rejected.

## Operational implications
New capabilities require catalog evidence, models, transforms, fixtures, and tests.
