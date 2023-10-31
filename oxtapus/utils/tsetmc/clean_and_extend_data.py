import polars as pl
from oxtapus.utils.http import requests, async_requests
from oxtapus.utils import json_normalize, manipulation_cols
from oxtapus.tsetmc.tsetmc import URL, cols

url = URL()


def market_watch(sections: list[str]):
    r = requests(url.mw(sections), response="json").get("marketwatch")
    df = pl.from_dicts(json_normalize(r, "blDs", "ob_"), schema_overrides={"pe": pl.Utf8})
    df = manipulation_cols(df, cols=cols.mw_orderbook)
    df = manipulation_cols(df, cols=cols.mw)
    return df
