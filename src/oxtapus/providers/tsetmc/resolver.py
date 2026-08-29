"""Strict instrument resolution with ambiguity preservation."""

from __future__ import annotations

from collections.abc import Iterable

from oxtapus.domain.enums import InstrumentState
from oxtapus.domain.errors import AmbiguousInstrumentError, InstrumentNotFoundError
from oxtapus.domain.identifiers import IdentifierKind, classify_identifier, normalize_persian
from oxtapus.domain.instruments import Instrument
from oxtapus.progress.reporter import ProgressReporter
from oxtapus.providers.tsetmc.provider import AsyncTsetmcProvider, TsetmcProvider
from oxtapus.providers.tsetmc.queries import (
    InstrumentInfoQuery,
    InstrumentSearchQuery,
    MarketWatchQuery,
)


class InstrumentResolver:
    """Resolve symbols and identifiers without choosing arbitrary matches."""

    def __init__(self, provider: TsetmcProvider) -> None:
        self._provider = provider
        self._cache: dict[str, Instrument] = {}

    def resolve(
        self, identifier: str, *, reporter: ProgressReporter, operation_id: str
    ) -> Instrument:
        """Resolve one identifier or raise a typed resolution error."""

        normalized = normalize_persian(identifier)
        if normalized in self._cache:
            return self._cache[normalized]
        kind = classify_identifier(normalized)
        if kind is IdentifierKind.TSETMC_INSTRUMENT_CODE:
            return self._fetch_info(normalized, reporter, operation_id)
        if kind is IdentifierKind.SYMBOL:
            result = self._provider.search(
                InstrumentSearchQuery(term=normalized),
                reporter=reporter,
                operation_id=operation_id,
            ).output.data
            exact = result.filter(result["symbol"] == normalized)
            if exact.height == 0:
                raise InstrumentNotFoundError(identifier)
            if exact.height > 1:
                raise AmbiguousInstrumentError(identifier, exact.to_dicts())
            return self._fetch_info(
                str(exact.item(0, "tsetmc_instrument_code")), reporter, operation_id
            )
        watch = self._provider.market_watch(
            MarketWatchQuery(), reporter=reporter, operation_id=operation_id
        ).output.data
        upper = normalized.upper()
        matches = watch.filter(
            watch["provider_instrument_id"].fill_null("").str.slice(0, 11) == upper[:11]
        )
        if matches.height == 0:
            raise InstrumentNotFoundError(identifier)
        if matches.height > 1:
            raise AmbiguousInstrumentError(identifier, matches.to_dicts())
        return self._fetch_info(
            str(matches.item(0, "tsetmc_instrument_code")), reporter, operation_id
        )

    def resolve_bulk(
        self, identifiers: Iterable[str], *, reporter: ProgressReporter, operation_id: str
    ) -> tuple[Instrument, ...]:
        """Resolve all identifiers in caller order."""

        return tuple(
            self.resolve(item, reporter=reporter, operation_id=operation_id) for item in identifiers
        )

    def _fetch_info(self, code: str, reporter: ProgressReporter, operation_id: str) -> Instrument:
        frame = self._provider.info(
            InstrumentInfoQuery(tsetmc_instrument_code=code),
            reporter=reporter,
            operation_id=operation_id,
        ).output.data
        if frame.height != 1:
            raise InstrumentNotFoundError(code)
        instrument = _instrument_from_record(frame.to_dicts()[0])
        self._remember(instrument)
        return instrument

    def _remember(self, instrument: Instrument) -> None:
        for value in (
            instrument.symbol,
            instrument.tsetmc_instrument_code,
            instrument.isin,
            instrument.provider_instrument_id,
        ):
            if value:
                self._cache[normalize_persian(value)] = instrument


class AsyncInstrumentResolver:
    """Native asynchronous counterpart of :class:`InstrumentResolver`."""

    def __init__(self, provider: AsyncTsetmcProvider) -> None:
        self._provider = provider
        self._cache: dict[str, Instrument] = {}

    async def resolve(
        self, identifier: str, *, reporter: ProgressReporter, operation_id: str
    ) -> Instrument:
        """Resolve one identifier without controlling the active event loop."""

        normalized = normalize_persian(identifier)
        if normalized in self._cache:
            return self._cache[normalized]
        kind = classify_identifier(normalized)
        if kind is IdentifierKind.TSETMC_INSTRUMENT_CODE:
            return await self._fetch_info(normalized, reporter, operation_id)
        if kind is IdentifierKind.SYMBOL:
            result = (
                await self._provider.search(
                    InstrumentSearchQuery(term=normalized),
                    reporter=reporter,
                    operation_id=operation_id,
                )
            ).output.data
            exact = result.filter(result["symbol"] == normalized)
            if exact.height == 0:
                raise InstrumentNotFoundError(identifier)
            if exact.height > 1:
                raise AmbiguousInstrumentError(identifier, exact.to_dicts())
            return await self._fetch_info(
                str(exact.item(0, "tsetmc_instrument_code")), reporter, operation_id
            )
        watch = (
            await self._provider.market_watch(
                MarketWatchQuery(), reporter=reporter, operation_id=operation_id
            )
        ).output.data
        upper = normalized.upper()
        matches = watch.filter(
            watch["provider_instrument_id"].fill_null("").str.slice(0, 11) == upper[:11]
        )
        if matches.height == 0:
            raise InstrumentNotFoundError(identifier)
        if matches.height > 1:
            raise AmbiguousInstrumentError(identifier, matches.to_dicts())
        return await self._fetch_info(
            str(matches.item(0, "tsetmc_instrument_code")), reporter, operation_id
        )

    async def _fetch_info(
        self, code: str, reporter: ProgressReporter, operation_id: str
    ) -> Instrument:
        frame = (
            await self._provider.info(
                InstrumentInfoQuery(tsetmc_instrument_code=code),
                reporter=reporter,
                operation_id=operation_id,
            )
        ).output.data
        if frame.height != 1:
            raise InstrumentNotFoundError(code)
        instrument = _instrument_from_record(frame.to_dicts()[0])
        for value in (
            instrument.symbol,
            instrument.tsetmc_instrument_code,
            instrument.isin,
            instrument.provider_instrument_id,
        ):
            if value:
                self._cache[normalize_persian(value)] = instrument
        return instrument


def _instrument_from_record(record: dict[str, object]) -> Instrument:
    state_value = str(record.get("state") or "unknown")
    return Instrument(
        tsetmc_instrument_code=str(record["tsetmc_instrument_code"]),
        symbol=str(record["symbol"]),
        instrument_name=str(record["instrument_name"]),
        isin=_value(record.get("isin")),
        provider_instrument_id=_value(record.get("provider_instrument_id")),
        exchange=_value(record.get("exchange")),
        market=_value(record.get("market")),
        board=_value(record.get("board")),
        instrument_type=_value(record.get("instrument_type")),
        sector_code=_value(record.get("sector_code")),
        sector_name=_value(record.get("sector_name")),
        state=InstrumentState(state_value),
        source_symbol=_value(record.get("source_symbol")),
        source_name=_value(record.get("source_name")),
    )


def _value(value: object) -> str | None:
    return None if value is None else str(value)
