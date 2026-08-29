# Oxtapus

Oxtapus 1.0 provides a small Polars-first API backed by typed provider, transport, schema,
quality, lineage, and persistence boundaries.

Start with [installation](getting-started/installation.md), then run the
[quickstart](getting-started/quickstart.md). Production users should read the
[architecture](concepts/architecture.md), [provider](concepts/providers.md), and
[data-layer](concepts/data-layers.md) concepts before enabling persistence.

!!! warning "Source stability"
    The official website is an upstream dependency, not an Oxtapus service. Endpoints may
    change, throttle, or become unavailable. Inspect `FetchResult` and the endpoint catalog.
