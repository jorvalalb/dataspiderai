import pytest
from pathlib import Path

from dataspiderai.agents.screener_agent import _translate_filters, _extract_tickers

def test_translate_filters_all_categories():
    codes = _translate_filters("nasd", "sp500", "technology", "biotechnology", "usa")
    assert "exch_nasd" in codes
    assert "idx_sp500" in codes
    assert "sec_technology" in codes
    assert "ind_biotechnology" in codes
    assert "geo_usa" in codes

def test_translate_filters_specific():
    codes = _translate_filters("nyse", "djia", "energy", "biotechnology", "canada")
    assert "exch_nyse" in codes
    # El mapeo de "djia" produce "idx_dji"
    assert "idx_dji" in codes
    assert "sec_energy" in codes
    assert "ind_biotechnology" in codes
    assert "geo_canada" in codes

def test_translate_filters_invalid_raises():
    # ahora esperamos KeyError para claves inválidas
    with pytest.raises(KeyError):
        _translate_filters("invalid_exch", "sp500", "technology", "software", "usa")

@pytest.mark.asyncio
async def test_extract_tickers_from_fixture(monkeypatch):
    html = Path("tests/fixtures/screener_page1.html").read_text()
    import dataspiderai.agents.screener_agent as sa

    async def fake_llm(snippet, prompt, model=None):
        return '["AAPL","MSFT","GOOG"]'
    monkeypatch.setattr(sa, "extract_with_llm", fake_llm)

    tickers = await _extract_tickers(html)
    assert tickers == ["AAPL", "MSFT", "GOOG"]
