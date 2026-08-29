"""Optional persistence backends."""

from oxtapus.storage.memory import MemoryStorage
from oxtapus.storage.parquet import LocalParquetStorage

__all__ = ["LocalParquetStorage", "MemoryStorage"]
