"""Conservative opt-in live source canary."""

import pytest

from oxtapus import Client, Settings


@pytest.mark.live
def test_official_instrument_search_canary() -> None:
    with Client(Settings(requests_per_second=1, retry_max_attempts=2)) as client:
        result = client.instruments.fetch_search("فولاد")
    assert result.data.height > 0
    assert "tsetmc_instrument_code" in result.data.columns
    assert result.source_schema_version
