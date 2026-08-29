"""Conservative opt-in endpoint probe; never imported by package runtime."""

from __future__ import annotations

import json
import sys

from oxtapus import Client, Settings


def main() -> int:
    """Probe one small search and print operational metadata without source payloads."""

    with Client(Settings(progress=False, requests_per_second=1)) as client:
        result = client.instruments.fetch_search("فولاد")
    sys.stdout.write(
        json.dumps(
            {
                "provider": result.provider,
                "capability": result.capability.value,
                "endpoint": result.endpoint,
                "rows": result.data.height,
                "retrieved_at": result.retrieved_at.isoformat(),
                "elapsed": result.elapsed,
                "retry_count": result.retry_count,
                "source_schema_version": result.source_schema_version,
                "warnings": result.warnings,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
