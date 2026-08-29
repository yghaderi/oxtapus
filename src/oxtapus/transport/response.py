"""Response plausibility helpers."""

from oxtapus.domain.errors import ResponseValidationError

_BLOCK_MARKERS = ("General Error Detected", "دسترسی شما", "مسدود")


def validate_response_body(content: bytes, content_type: str | None) -> None:
    """Reject empty, blocked, or HTML responses presented as source data."""

    if not content:
        raise ResponseValidationError("The upstream response body is empty.")
    preview = content[:4096].decode("utf-8", errors="ignore")
    if any(marker in preview for marker in _BLOCK_MARKERS):
        raise ResponseValidationError("The upstream host returned an access-block response.")
    if "text/html" in (content_type or "").lower() or preview.lstrip().lower().startswith(
        "<!doctype html"
    ):
        raise ResponseValidationError("The upstream host returned HTML instead of source data.")
