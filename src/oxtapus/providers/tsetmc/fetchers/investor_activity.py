"""Per-instrument investor-activity fetcher."""

from oxtapus.providers.base import TransformOutput
from oxtapus.providers.tsetmc.fetchers.base import BaseTsetmcFetcher
from oxtapus.providers.tsetmc.parsers import parse_object
from oxtapus.providers.tsetmc.queries import InvestorActivityQuery
from oxtapus.providers.tsetmc.transformers import transform_investor_activity
from oxtapus.transport.base import RawResponse


class InvestorActivityFetcher(BaseTsetmcFetcher[InvestorActivityQuery]):
    """Fetch current individual/institutional activity for one instrument."""

    def transform_query(self, query: InvestorActivityQuery) -> InvestorActivityQuery:
        return InvestorActivityQuery.model_validate(query.model_dump())

    def transform(self, response: RawResponse, query: InvestorActivityQuery) -> TransformOutput:
        return transform_investor_activity(
            parse_object(response, self.endpoint.response_envelope),
            query,
            response.retrieved_at,
        )

    def _url(self, query: InvestorActivityQuery) -> str:
        return self.endpoint.url_template.format(
            tsetmc_instrument_code=query.tsetmc_instrument_code
        )
