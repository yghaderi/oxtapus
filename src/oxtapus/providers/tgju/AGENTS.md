# TGJU provider rules

Read the root `AGENTS.md` before changing this bounded context.

- Use only verified routes and mappings recorded in the endpoint catalog.
- The endpoint catalog is evidence, not a wish list. Defaults use verified entries only.
- Never add scraping fallbacks, browser impersonation, authentication bypasses, or hidden routes.
- Extraction never persists and transformation never performs remote access.
- Preserve integral IRR prices as integers and missing source values as null.
- Keep sanitized offline fixtures and native synchronous/asynchronous parity.
