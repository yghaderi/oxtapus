# Storage

`MemoryStorage` is the zero-configuration default for tests and notebook workflows.
`LocalParquetStorage` writes Zstandard Parquet into Hive-style partitions using temporary
files followed by atomic replacement, merges primary keys, and writes a checksum manifest.
`DuckDBStorage` is optional and adds embedded SQL over Parquet.

Choose with `OXTAPUS_STORAGE_BACKEND`; storage never performs source extraction.
