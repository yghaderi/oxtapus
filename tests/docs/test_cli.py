"""CLI commands remain thin, offline where possible, and English."""

from oxtapus.cli.app import main, parser


def test_cli_dataset_and_capability_lists(capsys) -> None:
    assert main(["datasets", "list"]) == 0
    assert "daily_price" in capsys.readouterr().out
    assert main(["capabilities", "list"]) == 0
    assert "daily_prices" in capsys.readouterr().out


def test_cli_help_is_english() -> None:
    help_text = parser().format_help()
    assert "Typed Iranian financial market data" in help_text
    assert "capabilities" in help_text


def test_cli_parses_source_qualified_tgju_daily_prices() -> None:
    arguments = parser().parse_args(
        ["fetch", "tgju", "daily-prices", "دلار نیما", "--start", "1403/10/12"]
    )
    assert arguments.source == "tgju"
    assert arguments.command == "daily-prices"
    assert arguments.asset == "دلار نیما"
    assert arguments.start == "1403/10/12"
