# Architecture

Oxtapus uses lightweight hexagonal boundaries. API and CLI adapt user input; application
services coordinate use cases; domain objects contain financial language; provider adapters
own source-specific parsing; transport owns HTTPX2, retries, rate limits, and byte progress;
storage owns persistence.

:::{mermaid}
flowchart TD
    U[User API or CLI] --> A[Application]
    A --> D[Domain contracts]
    A --> P[Provider port]
    P --> X[Source adapter]
    X --> T[Transport port]
    A --> S[Storage port]
:::

Dependencies point inward. Provider transformation performs no I/O, extraction performs no
persistence, and Gold transformation performs no network access.
