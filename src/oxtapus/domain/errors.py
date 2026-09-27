"""Public exception hierarchy."""

from collections.abc import Sequence


class OxtapusError(Exception):
    """کلاس پایهٔ همهٔ خطاهای بسته."""


class ConfigurationError(OxtapusError):
    """تنظیمات نامعتبر یا ناامن است."""


class UnsupportedCapabilityError(OxtapusError):
    """فراهم‌کننده قابلیت درخواستی را پیاده‌سازی نکرده است."""


class EndpointUnavailableError(OxtapusError):
    """هیچ نقطهٔ پایانی تأییدشده‌ای برای قابلیت درخواستی در دسترس نیست."""


class TransportError(OxtapusError):
    """درخواست پیش از دریافت پاسخ معتبر شکست خورده است."""


class HTTPResponseError(TransportError):
    """سرور منبع پاسخ ناموفق HTTP برگردانده است."""

    def __init__(self, status_code: int, url: str, message: str) -> None:
        self.status_code = status_code
        self.url = url
        super().__init__(f"HTTP {status_code} from {url}: {message}")


class RetryExhaustedError(TransportError):
    """درخواست پس از همهٔ تلاش‌های مجاز همچنان ناموفق بوده است."""

    def __init__(self, attempts: int, original: BaseException) -> None:
        self.attempts = attempts
        self.original = original
        super().__init__(f"Request failed after {attempts} attempts: {original}")


class ResponseValidationError(OxtapusError):
    """بدنهٔ پاسخ ناقص یا از نظر معنایی نامعتبر است."""


class SchemaValidationError(ResponseValidationError):
    """رکورد منبع یا رکورد استاندارد با قرارداد طرح‌واره سازگار نیست."""


class SchemaDriftError(SchemaValidationError):
    """طرح‌وارهٔ منبع با وجود سیاست سخت‌گیرانه تغییر کرده است."""


class DataQualityError(OxtapusError):
    """دادهٔ استاندارد یکی از قواعد خطای کیفیت را نقض کرده است."""


class StorageError(OxtapusError):
    """عملیات ذخیره‌سازی به‌شکل کنترل‌شده شکست خورده است."""


class InstrumentResolutionError(OxtapusError):
    """کلاس پایهٔ خطاهای شناسایی ابزار مالی."""


class InstrumentNotFoundError(InstrumentResolutionError):
    """هیچ ابزار مالی با شناسهٔ واردشده پیدا نشده است."""

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier
        super().__init__(f"No instrument matches {identifier!r}.")


class InvalidInstrumentIdentifierError(InstrumentResolutionError):
    """قالب شناسهٔ ابزار مالی معتبر نیست."""


class UnsupportedAssetError(OxtapusError):
    """دارایی درخواستی در فهرست تأییدشده وجود ندارد."""

    def __init__(self, asset: str, supported: Sequence[str]) -> None:
        self.asset = asset
        self.supported = tuple(supported)
        choices = ", ".join(self.supported)
        super().__init__(f"Unsupported asset input {asset!r}. Supported assets: {choices}.")


class AmbiguousInstrumentError(InstrumentResolutionError):
    """شناسهٔ واردشده با بیش از یک ابزار مالی منطبق است."""

    def __init__(self, identifier: str, candidates: Sequence[object]) -> None:
        self.identifier = identifier
        self.candidates = tuple(candidates)
        super().__init__(
            f"Instrument identifier {identifier!r} is ambiguous; "
            f"{len(self.candidates)} candidates matched."
        )


class PartialFailureError(OxtapusError):
    """یک یا چند مورد در حالت توقف با اولین خطا شکست خورده‌اند."""


class PartialFetchWarning(UserWarning):
    """درخواست گروهی با وجود شکست بعضی موارد، بخشی از داده را برگردانده است."""
