import pytest
from pathlib import Path

from dataspiderai.agents.patent_agent import extract_patent_count, scrape_patents

@pytest.mark.asyncio
async def test_extract_patent_count_from_fixture(monkeypatch):
    html = Path("tests/fixtures/patents_quantum.html").read_text()
    import dataspiderai.agents.patent_agent as pa

    async def fake_llm(snippet, prompt):
        return '```json\n"More than 10 000 results"\n```'
    monkeypatch.setattr(pa, "extract_with_llm", fake_llm)

    phrase = await extract_patent_count(html)
    # ahora comprobamos la frase entera dentro del resultado
    assert "More than 10 000 results" in phrase

@pytest.mark.asyncio
async def test_scrape_patents_pipeline(monkeypatch):
    import dataspiderai.agents.patent_agent as pa
    html = Path("tests/fixtures/patents_quantum.html").read_text()

    # stub fetch_patents_html
    async def fake_fetch(query, start_date, end_date, engine):
        return html
    monkeypatch.setattr(pa, "fetch_patents_html", fake_fetch)

    # stub extract_with_llm
    async def fake_llm(snippet, prompt):
        return '```json\n"5 results"\n```'
    monkeypatch.setattr(pa, "extract_with_llm", fake_llm)

    res = await scrape_patents("quantum", None, None, engine="firefox")
    assert isinstance(res, dict)
    # count_phrase debe contener "5 results"
    assert "5 results" in res["count_phrase"]
    assert isinstance(res["count"], int)
    # Y debe incluir la marca scraped_at
    assert "scraped_at" in res
