from dataclasses import dataclass
import polars as pl


@dataclass
class ManipulationCols:
    rename: dict | None
    prefix: str | None
    suffix: str | None
    select: list[str] | None
    drop: list[str] | None


def manipulation_cols(df: pl.DataFrame, cols: ManipulationCols):
    if cols.rename:
        df = df.rename(cols.rename)
    if cols.prefix:
        df = df.rename({i: f"{cols.prefix}{i}" for i in df.columns})
    if cols.suffix:
        df = df.rename({i: f"{i}{cols.suffix}" for i in df.columns})
    if cols.select:
        df = df.select(cols.select)
    if cols.drop:
        df = df.drop(cols.drop)
    return df
