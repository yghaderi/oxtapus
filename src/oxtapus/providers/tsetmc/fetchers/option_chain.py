"""Option-chain fetcher."""

from oxtapus.providers.base import TransformOutput
from oxtapus.providers.tsetmc.fetchers.base import BaseTsetmcFetcher
from oxtapus.providers.tsetmc.parsers import parse_records
from oxtapus.providers.tsetmc.queries import OptionChainQuery
from oxtapus.providers.tsetmc.transformers import transform_option_chain
from oxtapus.transport.base import RawResponse


class OptionChainFetcher(BaseTsetmcFetcher[OptionChainQuery]):
    """Fetch paired option quotes and emit one canonical row per contract."""

    def transform_query(self, query: OptionChainQuery) -> OptionChainQuery:
        return OptionChainQuery.model_validate(query.model_dump())

    def transform(self, response: RawResponse, query: OptionChainQuery) -> TransformOutput:
        return transform_option_chain(
            parse_records(response, self.endpoint.response_envelope), query
        )

    def _url(self, query: OptionChainQuery) -> str:
        return self.endpoint.url_template
