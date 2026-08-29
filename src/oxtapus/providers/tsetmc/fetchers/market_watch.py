"""Market-watch fetcher."""

from oxtapus.providers.base import TransformOutput
from oxtapus.providers.tsetmc.fetchers.base import BaseTsetmcFetcher
from oxtapus.providers.tsetmc.parsers import parse_records
from oxtapus.providers.tsetmc.queries import MarketWatchQuery
from oxtapus.providers.tsetmc.transformers import transform_market_watch
from oxtapus.transport.base import RawResponse

_PAPER_TYPES = {"equity": 1, "etf": 8}


class MarketWatchFetcher(BaseTsetmcFetcher[MarketWatchQuery]):
    """Fetch a verified bulk snapshot for equities and ETFs."""

    def transform_query(self, query: MarketWatchQuery) -> MarketWatchQuery:
        normalized = MarketWatchQuery.model_validate(query.model_dump())
        unknown = set(normalized.instrument_types) - set(_PAPER_TYPES)
        if unknown:
            raise ValueError(f"Unverified instrument types: {sorted(unknown)}")
        if not normalized.instrument_types:
            raise ValueError("At least one instrument type is required.")
        return normalized

    def transform(self, response: RawResponse, query: MarketWatchQuery) -> TransformOutput:
        return transform_market_watch(
            parse_records(response, self.endpoint.response_envelope), query, response.retrieved_at
        )

    def _url(self, query: MarketWatchQuery) -> str:
        return self.endpoint.url_template

    def _params(self, query: MarketWatchQuery) -> dict[str, str | int | float | bool]:
        params: dict[str, str | int | float | bool] = {
            "market": 0,
            "industrialGroup": "",
            "showTraded": "false",
            "withBestLimits": "true",
        }
        params.update(
            {
                f"paperTypes[{index}]": _PAPER_TYPES[item]
                for index, item in enumerate(query.instrument_types)
            }
        )
        return params
