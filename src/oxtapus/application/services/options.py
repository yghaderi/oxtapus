"""Option selection preparation shared by retrieval and persisted ingestion."""

from oxtapus.domain.identifiers import IdentifierKind, classify_identifier
from oxtapus.progress.reporter import ProgressReporter
from oxtapus.providers.tsetmc.queries import OptionChainQuery
from oxtapus.providers.tsetmc.resolver import AsyncInstrumentResolver, InstrumentResolver


def option_chain_query(
    underlyings: tuple[str, ...],
    resolver: InstrumentResolver,
    *,
    reporter: ProgressReporter,
    operation_id: str,
) -> OptionChainQuery:
    """Use snapshot symbols/codes directly; resolve identifiers absent from the snapshot."""

    selections: list[str] = []
    for identifier in underlyings:
        if classify_identifier(identifier) in {
            IdentifierKind.SYMBOL,
            IdentifierKind.TSETMC_INSTRUMENT_CODE,
        }:
            selections.append(identifier)
        else:
            instrument = resolver.resolve(identifier, reporter=reporter, operation_id=operation_id)
            selections.append(instrument.tsetmc_instrument_code)
    return OptionChainQuery(underlyings=tuple(selections))


async def option_chain_query_async(
    underlyings: tuple[str, ...],
    resolver: AsyncInstrumentResolver,
    *,
    reporter: ProgressReporter,
    operation_id: str,
) -> OptionChainQuery:
    """Prepare the same selection using native asynchronous identifier resolution."""

    selections: list[str] = []
    for identifier in underlyings:
        if classify_identifier(identifier) in {
            IdentifierKind.SYMBOL,
            IdentifierKind.TSETMC_INSTRUMENT_CODE,
        }:
            selections.append(identifier)
        else:
            instrument = await resolver.resolve(
                identifier, reporter=reporter, operation_id=operation_id
            )
            selections.append(instrument.tsetmc_instrument_code)
    return OptionChainQuery(underlyings=tuple(selections))
