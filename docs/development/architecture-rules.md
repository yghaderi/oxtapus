# Architecture rules

Read root `AGENTS.md` and the nearest bounded-context rules before edits. Domain cannot import
API, application, provider, transport, or storage. Transport cannot know provider or financial
schemas. Storage cannot extract. Fetcher extraction cannot persist; fetcher transformation
cannot request; Gold cannot access the network. API and CLI call application services.

`uv run lint-imports` enforces core boundaries. Unit and contract tests also inspect the
surface and packaged catalogs.
