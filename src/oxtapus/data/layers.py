"""Material Bronze records and replay boundaries."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class BronzeRecord:
    """Append-only replay record for one provider response."""

    provider: str
    capability: str
    endpoint: str
    request_id: str
    run_id: str
    retrieved_at: datetime
    source_timezone: str
    package_version: str
    endpoint_catalog_version: str
    latency_seconds: float
    retry_count: int
    response_status: int
    response_headers: dict[str, str]
    content_type: str | None
    content_encoding: str | None
    content_length: int
    etag: str | None
    last_modified: str | None
    payload_checksum: str
    source_schema_fingerprint: str
    parser_version: str
    payload: bytes

    def metadata(self) -> dict[str, Any]:
        """Return persistable metadata without including the payload body."""

        values = asdict(self)
        values.pop("payload")
        return values

    def verify_checksum(self) -> bool:
        """Verify persisted payload integrity."""

        return hashlib.sha256(self.payload).hexdigest() == self.payload_checksum
