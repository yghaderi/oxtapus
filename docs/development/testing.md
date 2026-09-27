# Testing

Ordinary CI is fully offline and uses small sanitized source fixtures. Run:

```bash
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run lint-imports
uv run pytest -m "not live"
uv run sphinx-build -W --keep-going -b html docs docs/_build/html
uv build
```

Transport tests use HTTPX2 mock transports. Contract tests cover envelopes and catalogs;
storage tests prove idempotency, atomic replacement, checkpoints, and Bronze replay with no
network call. `pytest -m live` is opt-in and conservative.
