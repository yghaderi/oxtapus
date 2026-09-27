"""Verified TSETMC fetchers."""

from oxtapus.providers.tsetmc.fetchers.board_members import BoardMembersFetcher
from oxtapus.providers.tsetmc.fetchers.daily_prices import DailyPricesFetcher
from oxtapus.providers.tsetmc.fetchers.instrument import (
    InstrumentInfoFetcher,
    InstrumentSearchFetcher,
)
from oxtapus.providers.tsetmc.fetchers.instrument_identity import InstrumentIdentityFetcher
from oxtapus.providers.tsetmc.fetchers.investor_activity import InvestorActivityFetcher
from oxtapus.providers.tsetmc.fetchers.market_watch import MarketWatchFetcher
from oxtapus.providers.tsetmc.fetchers.option_chain import OptionChainFetcher
from oxtapus.providers.tsetmc.fetchers.order_book import OrderBookFetcher
from oxtapus.providers.tsetmc.fetchers.quote import QuoteFetcher

__all__ = [
    "BoardMembersFetcher",
    "DailyPricesFetcher",
    "InstrumentIdentityFetcher",
    "InstrumentInfoFetcher",
    "InstrumentSearchFetcher",
    "InvestorActivityFetcher",
    "MarketWatchFetcher",
    "OptionChainFetcher",
    "OrderBookFetcher",
    "QuoteFetcher",
]
