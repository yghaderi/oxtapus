"""Supported TGJU asset identifiers and user-facing aliases."""

from __future__ import annotations

from dataclasses import dataclass

from oxtapus.domain.errors import UnsupportedAssetError
from oxtapus.domain.identifiers import normalize_persian


@dataclass(frozen=True, slots=True)
class TgjuAsset:
    """One verified asset mapping owned by the provider."""

    code: str
    name: str
    source_id: str
    unit: str
    aliases: tuple[str, ...]


ASSETS = (
    TgjuAsset(
        code="usd_irr",
        name="دلار آزاد",
        source_id="price_dollar_rl",
        unit="one_us_dollar",
        aliases=("usd_irr", "دلار", "دلار آزاد"),
    ),
    TgjuAsset(
        code="nima_usd_irr",
        name="دلار نیما",
        source_id="nima_sell_usd",
        unit="one_us_dollar",
        aliases=("nima_usd_irr", "دلار نیما", "دلار نیمایی"),
    ),
    TgjuAsset(
        code="eur_irr",
        name="یورو",
        source_id="price_eur",
        unit="one_euro",
        aliases=("eur_irr", "یورو"),
    ),
    TgjuAsset(
        code="emami_gold_coin",
        name="سکه امامی",
        source_id="sekee",
        unit="one_coin",
        aliases=(
            "emami_gold_coin",
            "سکه امامی",
        ),
    ),
    TgjuAsset(
        code="half_gold_coin",
        name="نیم سکه",
        source_id="nim",
        unit="one_coin",
        aliases=(
            "half_gold_coin",
            "نیم سکه",
            "نیم‌سکه",
        ),
    ),
)


def _alias_key(value: str) -> str:
    """Normalize spelling, whitespace, and joiner variants for asset lookup."""

    return normalize_persian(value).casefold().replace(" ", "")


_BY_ALIAS = {_alias_key(alias): asset for asset in ASSETS for alias in asset.aliases}
_BY_CODE = {asset.code: asset for asset in ASSETS}


def resolve_asset(value: str) -> TgjuAsset:
    """Resolve one documented English or Persian asset alias."""

    normalized = _alias_key(value)
    try:
        return _BY_ALIAS[normalized]
    except KeyError as exc:
        supported = tuple(f"{asset.code} ({asset.name})" for asset in ASSETS)
        raise UnsupportedAssetError(value, supported) from exc


def asset_by_code(code: str) -> TgjuAsset:
    """Return one already-canonical asset."""

    return _BY_CODE[code]
