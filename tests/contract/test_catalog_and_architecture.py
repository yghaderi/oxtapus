"""Packaged catalogs and architectural boundary tests."""

from pathlib import Path

from oxtapus.data.catalog import DataCatalog
from oxtapus.domain.enums import EndpointStatus
from oxtapus.providers.tsetmc.capabilities import EndpointCatalog


def test_endpoint_catalog_is_fail_closed_and_evidenced() -> None:
    catalog = EndpointCatalog.load()
    endpoints = catalog.all()
    assert len(endpoints) >= 7
    assert all(item.last_verified_timestamp.tzinfo is not None for item in endpoints)
    assert all(len(item.schema_fingerprint) == 64 for item in endpoints)
    assert all(item.host == "https://cdn.tsetmc.com" for item in endpoints)
    assert catalog.get("daily_prices").status is EndpointStatus.VERIFIED


def test_data_catalog_has_all_material_layers() -> None:
    specs = DataCatalog.load().list()
    assert {item.name for item in specs} >= {
        "instrument",
        "daily_price",
        "market_watch",
        "market_snapshot",
        "option_quote",
        "option_chain",
    }
    assert {item.layer.value for item in specs} == {"silver", "gold"}


def test_source_layout_has_no_compatibility_tree() -> None:
    package = Path(__file__).parents[2] / "src" / "oxtapus"
    assert not (package / "compatibility").exists()
    assert not (package / "legacy").exists()
