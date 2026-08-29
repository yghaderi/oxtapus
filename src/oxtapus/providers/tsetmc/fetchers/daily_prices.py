"""Daily-price fetcher."""

from oxtapus.providers.base import TransformOutput
from oxtapus.providers.tsetmc.fetchers.base import BaseTsetmcFetcher
from oxtapus.providers.tsetmc.parsers import parse_records
from oxtapus.providers.tsetmc.queries import DailyPriceQuery
from oxtapus.providers.tsetmc.transformers import transform_daily_prices
from oxtapus.transport.base import RawResponse


class DailyPricesFetcher(BaseTsetmcFetcher[DailyPriceQuery]):
    """Fetch and canonicalize daily OHLCV for one resolved instrument."""

    def transform_query(self, query: DailyPriceQuery) -> DailyPriceQuery:
        normalized = DailyPriceQuery.model_validate(query.model_dump())
        if normalized.start and normalized.end and normalized.start > normalized.end:
            raise ValueError("start must be on or before end")
        return normalized

    def transform(self, response: RawResponse, query: DailyPriceQuery) -> TransformOutput:
        return transform_daily_prices(
            parse_records(response, self.endpoint.response_envelope), query
        )

    def _url(self, query: DailyPriceQuery) -> str:
        return self.endpoint.url_template.format(
            tsetmc_instrument_code=query.tsetmc_instrument_code
        )
