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
