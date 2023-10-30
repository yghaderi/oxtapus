import polars as pl
from oxtapus.utils.http import requests, async_requests
from oxtapus.utils import json_normalize, manipulation_cols
from oxtapus.tsetmc.utils import URL, cols


class Base:
    def __init__(self):
        self.url = URL()

    def _mw(self, sections):
        r = requests(self.url.mw(sections), response="json").get("marketwatch")
        df = pl.from_dicts(json_normalize(r, "blDs"), schema_overrides={"pe": pl.Utf8})
        return manipulation_cols(df, cols=cols.mw)


class Options(Base):

    def mw(self):
        df = self._mw(["options"])
        return manipulation_cols(df, cols=cols.options_mw)

    def info(self):
        pass
