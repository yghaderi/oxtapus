from dataclasses import dataclass
from polars import DataFrame


@dataclass
class ManipulationCols:
    rename: dict | None
    select: list[str] | None
    drop: list[str] | None


def manipulation_cols(df: DataFrame, cols: ManipulationCols):
    if cols.rename:
        df = df.rename(cols.rename)
    if cols.select:
        df = df.select(cols.select)
    if cols.drop:
        df = df.drop(cols.drop)
    return df
