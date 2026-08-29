"""Instrument search and identity fetchers."""

from urllib.parse import quote

from oxtapus.providers.base import TransformOutput
from oxtapus.providers.tsetmc.fetchers.base import BaseTsetmcFetcher
from oxtapus.providers.tsetmc.parsers import parse_object, parse_records
from oxtapus.providers.tsetmc.queries import InstrumentInfoQuery, InstrumentSearchQuery
from oxtapus.providers.tsetmc.transformers import (
    transform_instrument_info,
    transform_instrument_search,
)
from oxtapus.transport.base import RawResponse


class InstrumentSearchFetcher(BaseTsetmcFetcher[InstrumentSearchQuery]):
    """Search instruments from a normalized user term."""

    def transform_query(self, query: InstrumentSearchQuery) -> InstrumentSearchQuery:
        return InstrumentSearchQuery.model_validate(query.model_dump())

    def transform(self, response: RawResponse, query: InstrumentSearchQuery) -> TransformOutput:
        return transform_instrument_search(parse_records(response, self.endpoint.response_envelope))

    def _url(self, query: InstrumentSearchQuery) -> str:
        return self.endpoint.url_template.format(term=quote(query.term, safe=""))


class InstrumentInfoFetcher(BaseTsetmcFetcher[InstrumentInfoQuery]):
    """Fetch a complete instrument identity by TSETMC code."""

    def transform_query(self, query: InstrumentInfoQuery) -> InstrumentInfoQuery:
        return InstrumentInfoQuery.model_validate(query.model_dump())

    def transform(self, response: RawResponse, query: InstrumentInfoQuery) -> TransformOutput:
        return transform_instrument_info(parse_object(response, self.endpoint.response_envelope))

    def _url(self, query: InstrumentInfoQuery) -> str:
        return self.endpoint.url_template.format(
            tsetmc_instrument_code=query.tsetmc_instrument_code
        )
