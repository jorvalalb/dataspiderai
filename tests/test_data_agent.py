# tests/test_data_agent.py
import re
from pathlib import Path

import pytest
import pandas as pd

import dataspiderai.agents.data_agent as da
from dataspiderai.agents.data_agent import (
    extract_metrics,
    extract_insiders,
    _bs_statement_to_df
)


@pytest.mark.asyncio
async def test_extract_metrics_from_fixture(monkeypatch):
    html = Path("tests/fixtures/finviz_snapshot.html").read_text()

    # stub de _gpt_json para devolver dict directamente
    async def fake_gpt_json(snippet, prompt):
        return {"P/E": "15.2", "EPS (ttm)": "3.4"}
    monkeypatch.setattr(da, "_gpt_json", fake_gpt_json)

    metrics = await extract_metrics(html)
    assert isinstance(metrics, dict)
    assert metrics["P/E"] == "15.2"
    assert metrics["EPS (ttm)"] == "3.4"


@pytest.mark.asyncio
async def test_extract_insiders_from_fixture(monkeypatch):
    html = Path("tests/fixtures/finviz_snapshot.html").read_text()

    # stub de _gpt_json para devolver lista directamente
    async def fake_gpt_json(snippet, prompt):
        return [{"Insider": "J. Doe", "Transaction": "Buy"}]
    monkeypatch.setattr(da, "_gpt_json", fake_gpt_json)

    insiders = await extract_insiders(html)
    assert isinstance(insiders, list)
    first = insiders[0]
    assert first["Insider"] == "J. Doe"
    assert first["Transaction"] == "Buy"


def test_bs_statement_to_df_with_valid_html():
    html = (
        '<table data-testid="quote-statements-table">'
        '<tr><td>Metric</td><td>ignore</td><td>Val1</td><td>Val2</td></tr>'
        '<tr><td>Rev</td><td>ignore</td><td>100</td><td>200</td></tr>'
        '</table>'
    )
    df = _bs_statement_to_df(html)
    assert df is not None
    # ahora incluye columna 'extracted_at' entre Metric y valores
    expected_cols = ["Metric", "extracted_at", "Val1", "Val2"]
    assert list(df.columns) == expected_cols

    ts = df.loc[0, "extracted_at"]
    # acepta timestamp ISO (YYYY-MM-DDTHH:MM:SS…) o con guión bajo YYYY-MM-DD_HH-MM-SS
    assert re.match(r"\d{4}-\d{2}-\d{2}[T_]\d{2}:\d{2}:\d{2}", ts)


def test_bs_statement_to_df_with_invalid_html():
    assert _bs_statement_to_df(None) is None
    assert _bs_statement_to_df("<div>No table here</div>") is None


def test_bs_statement_to_df_multiple_rows_returns_none():
    """
    Cuando la tabla no contiene suficientes columnas
    para extraer valores (p.ej. solo una columna de datos),
    debe devolver None.
    """
    html = (
        '<table data-testid="quote-statements-table">'
        '<tr><td>Metric</td><td>ignore</td><td>Value</td></tr>'
        '<tr><td>X</td><td>ignore</td><td>10</td></tr>'
        '<tr><td>Y</td><td>ignore</td><td>20</td></tr>'
        '</table>'
    )
    df = _bs_statement_to_df(html)
    assert df is None
