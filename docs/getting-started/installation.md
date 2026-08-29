# Installation

Install the core on Python 3.11–3.14:

```bash
python -m pip install oxtapus
```

The core includes HTTPX2, Polars, Pydantic, and Pydantic Settings. Arrow, Pandas, DuckDB,
and HTTP/2 support are optional:

```bash
python -m pip install 'oxtapus[arrow,pandas,duckdb,http2]'
```

Confirm the clean installation with `python -c "import oxtapus; print(oxtapus.__version__)"`.
