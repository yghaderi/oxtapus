"""Small English CLI over the public application services."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict

import polars as pl

from oxtapus.api.client import Client
from oxtapus.api.settings import Settings
from oxtapus.application.services import IngestionRun
from oxtapus.data.catalog import DataCatalog
from oxtapus.data.schema import schema_diff
from oxtapus.providers.tsetmc.capabilities import EndpointCatalog


def parser() -> argparse.ArgumentParser:
    """Build the command tree without performing I/O."""

    root = argparse.ArgumentParser(
        prog="oxtapus",
        description="Typed Iranian financial market data.",
    )
    groups = root.add_subparsers(dest="group", required=True)

    datasets = groups.add_parser("datasets", help="Inspect canonical datasets.")
    datasets.add_subparsers(dest="command", required=True).add_parser(
        "list", help="List dataset contracts."
    )

    capabilities = groups.add_parser("capabilities", help="Inspect provider capabilities.")
    capabilities.add_subparsers(dest="command", required=True).add_parser(
        "list", help="List verified capabilities."
    )

    provider = groups.add_parser("provider", help="Inspect a provider.")
    providers = provider.add_subparsers(dest="provider", required=True)
    tsetmc = providers.add_parser("tsetmc", help="Official TSETMC website provider.")
    tsetmc_sub = tsetmc.add_subparsers(dest="command", required=True)
    tsetmc_sub.add_parser("doctor", help="Validate local configuration and endpoint catalog.")
    tsetmc_sub.add_parser("probe", help="Run a conservative instrument-search probe.")

    instruments = groups.add_parser("instruments", help="Discover instruments.")
    instrument_commands = instruments.add_subparsers(dest="command", required=True)
    search = instrument_commands.add_parser("search", help="Search instruments.")
    search.add_argument("term", help="Symbol or instrument name fragment.")

    fetch = groups.add_parser("fetch", help="Fetch canonical market data.")
    fetch_commands = fetch.add_subparsers(dest="command", required=True)
    daily = fetch_commands.add_parser("daily-prices", help="Fetch daily OHLCV.")
    daily.add_argument("symbols", nargs="+", help="Symbols or verified identifiers.")
    daily.add_argument("--start", help="First ISO date, inclusive.")
    daily.add_argument("--end", help="Last ISO date, inclusive.")
    watch = fetch_commands.add_parser("market-watch", help="Fetch the latest snapshot.")
    watch.add_argument(
        "--instrument-type",
        action="append",
        dest="instrument_types",
        choices=("equity", "etf"),
        help="Repeat to select instrument types.",
    )
    chain = fetch_commands.add_parser("option-chain", help="Fetch an option chain.")
    chain.add_argument("underlying", help="Underlying symbol or identifier.")

    ingest = groups.add_parser("ingest", help="Run configured incremental ingestion.")
    ingest.add_argument(
        "--dataset",
        choices=("daily_price", "market_snapshot", "option_chain"),
        default="market_snapshot",
        help="Dataset to ingest.",
    )
    ingest.add_argument("--symbol", action="append", help="Daily-price symbol; repeatable.")
    ingest.add_argument("--underlying", help="Option-chain underlying symbol.")
    ingest.add_argument("--start", help="First ISO date, inclusive.")
    ingest.add_argument("--end", help="Last ISO date, inclusive.")
    backfill = groups.add_parser("backfill", help="Backfill a configured date range.")
    backfill.add_argument("symbols", nargs="+", help="Daily-price symbols or identifiers.")
    backfill.add_argument("--start", required=True, help="First ISO date, inclusive.")
    backfill.add_argument("--end", required=True, help="Last ISO date, inclusive.")

    schemas = groups.add_parser("schemas", help="Inspect canonical schemas.")
    schema_commands = schemas.add_subparsers(dest="command", required=True)
    show = schema_commands.add_parser("show", help="Show a dataset contract.")
    show.add_argument("dataset", help="Dataset contract name.")
    diff = schema_commands.add_parser("diff", help="Diff two JSON schema signatures.")
    diff.add_argument("before", help="Path to the previous JSON signature.")
    diff.add_argument("after", help="Path to the current JSON signature.")

    storage = groups.add_parser("storage", help="Inspect configured storage.")
    storage_commands = storage.add_subparsers(dest="command", required=True)
    storage_commands.add_parser("inspect", help="Show storage configuration.")
    return root


def main(argv: Sequence[str] | None = None) -> int:
    """Execute one CLI command and return its process status."""

    arguments = parser().parse_args(argv)
    settings = Settings()
    if arguments.group == "datasets" and arguments.command == "list":
        for spec in DataCatalog.load().list():
            sys.stdout.write(f"{spec.name}\t{spec.layer.value}\t{spec.schema_version}\n")
        return 0
    if arguments.group == "capabilities" and arguments.command == "list":
        with Client(settings) as client:
            for capability in client.capabilities():
                sys.stdout.write(capability.value + "\n")
        return 0
    if arguments.group == "provider" and arguments.provider == "tsetmc":
        catalog = EndpointCatalog.load()
        if arguments.command == "doctor":
            rows = [
                {
                    "capability": endpoint.capability.value,
                    "endpoint": endpoint.name,
                    "status": endpoint.status.value,
                    "latency_seconds": None,
                    "response_validity": "not probed by offline doctor",
                    "schema_fingerprint": endpoint.schema_fingerprint,
                    "last_verified_timestamp": endpoint.last_verified_timestamp.isoformat(),
                    "parser_compatibility": "catalogued",
                    "warning_summary": endpoint.known_limitations,
                    "error_summary": None,
                }
                for endpoint in catalog.all()
            ]
            sys.stdout.write(json.dumps(rows, indent=2) + "\n")
            return 0
        if arguments.command == "probe":
            with Client(settings) as client:
                _print_frame(client.instruments.search("فولاد"))
            return 0
    if arguments.group == "instruments" and arguments.command == "search":
        with Client(settings) as client:
            _print_frame(client.instruments.search(arguments.term, progress=True))
        return 0
    if arguments.group == "fetch":
        with Client(settings) as client:
            if arguments.command == "daily-prices":
                _print_frame(
                    client.market.daily_prices(
                        arguments.symbols,
                        arguments.start,
                        arguments.end,
                        progress=True,
                    )
                )
            elif arguments.command == "market-watch":
                types = arguments.instrument_types or ["equity", "etf"]
                _print_frame(client.market.market_watch(types, progress=True))
            elif arguments.command == "option-chain":
                _print_frame(client.market.option_chain(arguments.underlying, progress=True))
        return 0
    if arguments.group == "ingest":
        with Client(settings) as client:
            if arguments.dataset == "market_snapshot":
                run = client.ingestion.market_watch(progress=True)
            elif arguments.dataset == "option_chain" and arguments.underlying:
                run = client.ingestion.option_chain(arguments.underlying, progress=True)
            elif arguments.dataset == "daily_price" and arguments.symbol:
                run = client.ingestion.daily_prices(
                    arguments.symbol,
                    arguments.start,
                    arguments.end,
                    progress=True,
                )
            else:
                sys.stderr.write(
                    "daily_price requires --symbol; option_chain requires --underlying.\n"
                )
                return 2
        _print_ingestion(run)
        return 0
    if arguments.group == "backfill":
        with Client(settings) as client:
            run = client.ingestion.daily_prices(
                arguments.symbols,
                arguments.start,
                arguments.end,
                progress=True,
            )
        _print_ingestion(run)
        return 0
    if arguments.group == "schemas":
        if arguments.command == "show":
            spec = DataCatalog.load().get(arguments.dataset)
            sys.stdout.write(json.dumps(asdict(spec), default=str, indent=2) + "\n")
        else:
            with open(arguments.before, encoding="utf-8") as before_file:
                before = json.load(before_file)
            with open(arguments.after, encoding="utf-8") as after_file:
                after = json.load(after_file)
            sys.stdout.write(json.dumps(asdict(schema_diff(before, after)), indent=2) + "\n")
        return 0
    if arguments.group == "storage" and arguments.command == "inspect":
        sys.stdout.write(
            json.dumps(
                {
                    "backend": settings.storage_backend,
                    "data_directory": str(settings.data_directory),
                    "persisted_layers": [item.value for item in settings.persisted_data_layers],
                },
                indent=2,
            )
            + "\n"
        )
        return 0
    return 2


def _print_frame(frame: pl.DataFrame) -> None:
    sys.stdout.write(frame.write_json() + "\n")


def _print_ingestion(run: IngestionRun) -> None:
    results = run.results
    failures = run.failures
    sys.stdout.write(
        json.dumps(
            {
                "successful_items": len(results),
                "failed_items": len(failures),
                "failures": [asdict(item) for item in failures],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    raise SystemExit(main())
