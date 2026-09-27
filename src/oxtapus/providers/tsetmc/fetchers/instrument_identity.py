"""Per-instrument source identity fetcher."""

from oxtapus.providers.base import TransformOutput
from oxtapus.providers.tsetmc.fetchers.base import BaseTsetmcFetcher
from oxtapus.providers.tsetmc.parsers import parse_object
from oxtapus.providers.tsetmc.queries import InstrumentIdentityQuery
from oxtapus.providers.tsetmc.transformers import transform_instrument_identity
from oxtapus.transport.base import RawResponse


class InstrumentIdentityFetcher(BaseTsetmcFetcher[InstrumentIdentityQuery]):
    """Fetch and canonicalize source identity and classification data."""

    def transform_query(self, query: InstrumentIdentityQuery) -> InstrumentIdentityQuery:
        return InstrumentIdentityQuery.model_validate(query.model_dump())

    def transform(self, response: RawResponse, query: InstrumentIdentityQuery) -> TransformOutput:
        return transform_instrument_identity(
            parse_object(response, self.endpoint.response_envelope),
            query,
        )

    def _url(self, query: InstrumentIdentityQuery) -> str:
        return self.endpoint.url_template.format(
            tsetmc_instrument_code=query.tsetmc_instrument_code
        )
