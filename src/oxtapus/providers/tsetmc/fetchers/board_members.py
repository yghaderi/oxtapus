"""Board-member disclosure fetcher."""

from oxtapus.providers.base import TransformOutput
from oxtapus.providers.tsetmc.fetchers.base import BaseTsetmcFetcher
from oxtapus.providers.tsetmc.parsers import parse_records
from oxtapus.providers.tsetmc.queries import BoardMembersQuery
from oxtapus.providers.tsetmc.transformers import transform_board_members
from oxtapus.transport.base import RawResponse


class BoardMembersFetcher(BaseTsetmcFetcher[BoardMembersQuery]):
    """Fetch and flatten verified board-member disclosure statements."""

    def transform_query(self, query: BoardMembersQuery) -> BoardMembersQuery:
        return BoardMembersQuery.model_validate(query.model_dump())

    def transform(self, response: RawResponse, query: BoardMembersQuery) -> TransformOutput:
        return transform_board_members(
            parse_records(response, self.endpoint.response_envelope),
            query,
        )

    def _url(self, query: BoardMembersQuery) -> str:
        return self.endpoint.url_template.format(
            tsetmc_instrument_code=query.tsetmc_instrument_code
        )
