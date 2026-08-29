"""Public exception hierarchy."""

from collections.abc import Sequence


class OxtapusError(Exception):
    """Base class for all package errors."""


class ConfigurationError(OxtapusError):
    """Configuration is invalid or unsafe."""


class UnsupportedCapabilityError(OxtapusError):
    """A provider does not implement the requested capability."""


class EndpointUnavailableError(OxtapusError):
    """No verified endpoint can serve the capability."""


class TransportError(OxtapusError):
    """A remote request failed before a valid response was produced."""


class HTTPResponseError(TransportError):
    """A remote server returned an unsuccessful HTTP response."""

    def __init__(self, status_code: int, url: str, message: str) -> None:
        self.status_code = status_code
        self.url = url
        super().__init__(f"HTTP {status_code} from {url}: {message}")


class RetryExhaustedError(TransportError):
    """A retryable request exhausted its configured retry policy."""

    def __init__(self, attempts: int, original: BaseException) -> None:
        self.attempts = attempts
        self.original = original
        super().__init__(f"Request failed after {attempts} attempts: {original}")


class ResponseValidationError(OxtapusError):
    """A response body is malformed or semantically implausible."""


class SchemaValidationError(ResponseValidationError):
    """A source or canonical record violates its schema contract."""


class SchemaDriftError(SchemaValidationError):
    """A source schema changed under a strict schema policy."""


class DataQualityError(OxtapusError):
    """Canonical data violates an error-level quality rule."""


class StorageError(OxtapusError):
    """A persistence operation failed safely."""


class InstrumentResolutionError(OxtapusError):
    """Base class for instrument-resolution errors."""


class InstrumentNotFoundError(InstrumentResolutionError):
    """No instrument matches an identifier."""

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier
        super().__init__(f"No instrument matches {identifier!r}.")


class InvalidInstrumentIdentifierError(InstrumentResolutionError):
    """An identifier has an invalid form."""


class AmbiguousInstrumentError(InstrumentResolutionError):
    """An identifier matches more than one instrument."""

    def __init__(self, identifier: str, candidates: Sequence[object]) -> None:
        self.identifier = identifier
        self.candidates = tuple(candidates)
        super().__init__(
            f"Instrument identifier {identifier!r} is ambiguous; "
            f"{len(self.candidates)} candidates matched."
        )


class PartialFailureError(OxtapusError):
    """One or more items failed in fail-fast mode."""


class PartialFetchWarning(UserWarning):
    """A simple batch call returned data while one or more items failed."""
