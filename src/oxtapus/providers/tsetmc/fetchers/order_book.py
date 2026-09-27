"""Per-instrument order-book fetcher."""

from oxtapus.providers.base import TransformOutput
from oxtapus.providers.tsetmc.fetchers.base import BaseTsetmcFetcher
from oxtapus.providers.tsetmc.parsers import parse_nullable_records
from oxtapus.providers.tsetmc.queries import OrderBookQuery
from oxtapus.providers.tsetmc.transformers import transform_order_book
from oxtapus.transport.base import RawResponse


class OrderBookFetcher(BaseTsetmcFetcher[OrderBookQuery]):
    """Fetch and canonicalize the five best bid/ask levels for one instrument."""

    def transform_query(self, query: OrderBookQuery) -> OrderBookQuery:
        return OrderBookQuery.model_validate(query.model_dump())

    def transform(self, response: RawResponse, query: OrderBookQuery) -> TransformOutput:
        return transform_order_book(
            parse_nullable_records(response, self.endpoint.response_envelope),
            query,
            response.retrieved_at,
        )

    def _url(self, query: OrderBookQuery) -> str:
        return self.endpoint.url_template.format(
            tsetmc_instrument_code=query.tsetmc_instrument_code
        )
