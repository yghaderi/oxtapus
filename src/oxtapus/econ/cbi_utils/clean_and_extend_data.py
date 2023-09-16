import pandas as pd


def clean_tsd_cbi(text: str):
    return pd.read_html(text)[0]
