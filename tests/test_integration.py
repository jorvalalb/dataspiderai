# tests/test_integration.py

import sys
import logging
import pytest
from pathlib import Path

from dataspiderai.cli import parse_args, run_pipeline

import dataspiderai.utils.agents_utils as au_utils
import dataspiderai.agents.patent_agent as pa_agent
import dataspiderai.agents.screener_agent as sc_agent

@pytest.mark.asyncio
async def test_cli_screener_mode(monkeypatch, tmp_path, caplog):
    # Configuramos el logger para capturar INFO
    caplog.set_level(logging.INFO, logger="dataspiderai")

    # Fixture de la página de screener
    screen_html = Path("tests/fixtures/screener_page1.html").read_text()

    # No necesitamos realmente patentes en este flujo
    monkeypatch.setattr(pa_agent, "fetch_patents_html", lambda *args, **kwargs: "")

    # Stub genérico de LLM para datos: métricas {} y tablas []
    async def fake_data_llm(snippet, prompt, model=None):
        if "snapshot metrics" in prompt:
            return "{}"
        return "[]"
    monkeypatch.setattr(au_utils, "extract_with_llm", fake_data_llm)
    monkeypatch.setattr(sc_agent, "extract_with_llm", fake_data_llm)

    # Stub de la página screener (sin Playwright)
    async def fake_fetch_screener(url, engine):
        return screen_html
    monkeypatch.setattr(sc_agent, "_fetch_html", fake_fetch_screener)

    # Devolvemos un ticker real
    async def fake_extract_tickers(html):
        return ["AAPL"]
    monkeypatch.setattr(sc_agent, "_extract_tickers", fake_extract_tickers)

    # Stub de scrape_company dentro de screener_agent para no abrir navegador
    async def fake_scrape_company(symbol, **kwargs):
        return {"metrics": {}, "insiders": [], "news": []}
    monkeypatch.setattr(sc_agent, "scrape_company", fake_scrape_company)

    # Preparamos argv solo con --screener
    monkeypatch.setenv("DATASPIDERAI_OUTPUT_FORMAT", "json")
    monkeypatch.setattr(sys, "argv", [
        "dataspiderai",
        "--screener", "1", "1",
        "--exch", "nasd",
        "--sector", "technology",
        "--industry", "semiconductors"
    ])

    args = parse_args()
    await run_pipeline(args)

    # Verificamos en los registros que se intentó scrappear "AAPL"
    messages = [rec.getMessage() for rec in caplog.records]
    assert any("↳ Scraping AAPL" in m for m in messages)
