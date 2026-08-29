# Contributing

Read `AGENTS.md` and the nearest bounded-context rules first. Create a focused change, add
offline tests, preserve canonical names and nulls, and keep unverified endpoints disabled.

Run the complete command set in `docs/development/testing.md`. Never commit payloads that
contain personal data, session state, credentials, cookies, or authorization headers. Endpoint
changes require first-party discovery evidence, a timestamp, fingerprint, negative cases, and
updated notices. Third-party code must not be copied; record license review for new references.
