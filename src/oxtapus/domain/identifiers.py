"""Instrument identifier normalization and classification."""

from __future__ import annotations

import re
import unicodedata
from enum import StrEnum

from oxtapus.domain.errors import InvalidInstrumentIdentifierError

_ZERO_WIDTH = dict.fromkeys(map(ord, "\u200b\u200c\u200d\ufeff"), None)
_ARABIC_TO_PERSIAN = str.maketrans({"ي": "ی", "ى": "ی", "ك": "ک"})
_WHITESPACE = re.compile(r"\s+")
_ISIN = re.compile(r"^[A-Z]{2}[A-Z0-9]{9}[0-9]$")
_PROVIDER_ID = re.compile(r"^[A-Z]{3}[A-Z0-9]{9}$")
_TSETMC_CODE = re.compile(r"^[0-9]{5,20}$")


class IdentifierKind(StrEnum):
    """Supported identifier families."""

    SYMBOL = "symbol"
    ISIN = "isin"
    PROVIDER_INSTRUMENT_ID = "provider_instrument_id"
    TSETMC_INSTRUMENT_CODE = "tsetmc_instrument_code"


def normalize_persian(value: str) -> str:
    """Normalize safe Persian/Arabic Unicode variants while preserving letters."""

    normalized = unicodedata.normalize("NFKC", value)
    normalized = normalized.translate(_ARABIC_TO_PERSIAN).translate(_ZERO_WIDTH)
    normalized = normalized.replace("\u00a0", " ")
    return _WHITESPACE.sub(" ", normalized).strip()


def classify_identifier(value: str) -> IdentifierKind:
    """Classify a non-empty instrument identifier without guessing."""

    candidate = normalize_persian(value)
    if not candidate:
        raise InvalidInstrumentIdentifierError("Instrument identifiers cannot be empty.")
    upper = candidate.upper()
    if _TSETMC_CODE.fullmatch(candidate):
        return IdentifierKind.TSETMC_INSTRUMENT_CODE
    if _ISIN.fullmatch(upper):
        return IdentifierKind.ISIN
    if _PROVIDER_ID.fullmatch(upper):
        return IdentifierKind.PROVIDER_INSTRUMENT_ID
    if any(char.isalpha() for char in candidate):
        return IdentifierKind.SYMBOL
    raise InvalidInstrumentIdentifierError(f"Invalid instrument identifier: {value!r}.")
