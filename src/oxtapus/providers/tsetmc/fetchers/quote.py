"""Per-instrument latest board quote fetcher."""

from oxtapus.providers.base import TransformOutput
from oxtapus.providers.tsetmc.fetchers.base import BaseTsetmcFetcher
from oxtapus.providers.tsetmc.parsers import parse_object
from oxtapus.providers.tsetmc.queries import QuoteQuery
from oxtapus.providers.tsetmc.transformers import transform_quote
from oxtapus.transport.base import RawResponse


class QuoteFetcher(BaseTsetmcFetcher[QuoteQuery]):
    """Fetch and canonicalize latest board data for one instrument."""

    def transform_query(self, query: QuoteQuery) -> QuoteQuery:
        return QuoteQuery.model_validate(query.model_dump())

    def transform(self, response: RawResponse, query: QuoteQuery) -> TransformOutput:
        return transform_quote(
            parse_object(response, self.endpoint.response_envelope),
            query,
        )

    def _url(self, query: QuoteQuery) -> str:
        return self.endpoint.url_template.format(
            tsetmc_instrument_code=query.tsetmc_instrument_code
        )
