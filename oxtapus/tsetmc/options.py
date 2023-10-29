import polars as pl
from oxtapus.utils.http import requests, async_requests
from oxtapus.tsetmc.utils import URL


class Base:
    def __init__(self):
        self.url = URL()

    def clean_mw(self, sections):
        main = requests(self.url.mw(sections), response="json")
        df = pl.read_json(main)
        return main


class Options(Base):

    def mw(self):
        df = self.clean_mw(sections=["options"])

    def info(self):
        pass

