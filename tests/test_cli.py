# tests/test_cli.py
import sys
import pytest

from dataspiderai.cli import parse_args

@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    monkeypatch.delenv("DATASPIDERAI_OUTPUT_FORMAT", raising=False)
    yield

def test_help_flag_exits(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["dataspiderai", "-h"])
    with pytest.raises(SystemExit) as exc:
        parse_args()
    assert exc.value.code == 0

def test_default_output_format(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["dataspiderai"])
    args = parse_args()
    assert args.output == "csv"

def test_output_flag_overrides_env(monkeypatch):
    monkeypatch.setenv("DATASPIDERAI_OUTPUT_FORMAT", "parquet")
    monkeypatch.setattr(sys, "argv", ["dataspiderai", "--output", "json"])
    args = parse_args()
    assert args.output == "json"

def test_parse_patents_only(monkeypatch):
    monkeypatch.setattr(
        sys, "argv",
        ["dataspiderai", "--patents", "quantum", "2024-01-01", "2024-12-31"]
    )
    args = parse_args()
    assert args.patents == ["quantum", "2024-01-01", "2024-12-31"]
    assert args.screener is None

def test_parse_screener_only(monkeypatch):
    monkeypatch.setattr(
        sys, "argv",
        ["dataspiderai", "--screener", "2024-01-01", "2024-12-31"]
    )
    args = parse_args()
    assert args.screener == ["2024-01-01", "2024-12-31"]
    assert args.patents is None

def test_metrics_flag_is_list(monkeypatch):
    """--metrics toma varios tokens y los devuelve en lista."""
    monkeypatch.setattr(
        sys, "argv",
        ["dataspiderai", "--metrics", "P/E", "ROE"]
    )
    args = parse_args()
    assert isinstance(args.metrics, list)
    assert args.metrics == ["P/E", "ROE"]

def test_metrics_flag_invalid_token_exits(monkeypatch):
    """Un token inválido en --metrics aborta con código 1."""
    monkeypatch.setattr(
        sys, "argv",
        ["dataspiderai", "--metrics", "EPS", "P/E"]
    )
    with pytest.raises(SystemExit) as exc:
        parse_args()
    assert exc.value.code == 1

def test_boolean_flags(monkeypatch):
    """El resto de flags (insiders, info, etc.) se parsean como booleanos."""
    flags = [
        "--insiders", "--info", "--managers",
        "--funds", "--ratings", "--news", "--holdings-bd",
        "--top10", "--income", "--balance", "--cash"
    ]
    monkeypatch.setattr(sys, "argv", ["dataspiderai"] + flags)
    args = parse_args()
    # todos deben ser True
    for attr in [
        "insiders", "info", "managers", "funds",
        "ratings", "news", "holdings_bd",
        "top10", "income", "balance", "cash"
    ]:
        assert getattr(args, attr) is True
    # metrics, al no pasarse, es None
    assert args.metrics is None

def test_symbol_positionals(monkeypatch):
    """Los argumentos posicionales no flags van a args.symbols."""
    monkeypatch.setattr(sys, "argv", ["dataspiderai", "AAPL", "MSFT", "--metrics", "P/E"])
    args = parse_args()
    assert args.symbols == ["AAPL", "MSFT"]
    assert args.metrics == ["P/E"]
