import pytest
from patent_agent import extract_patent_count

HTML_SIMPLE = '<div id="count">More than 100,000 results</div>'

class DummyLLM:
    async def __call__(self, snippet, prompt):
        # Return fence-wrapped phrase
        return "```json\nMore than 100,000 results\n```"

@pytest.mark.asyncio
async def test_extract_patent_count(monkeypatch):
    from agents_utils import extract_with_llm
    monkeypatch.setattr("patent_agent.extract_with_llm", DummyLLM())
    phrase = await extract_patent_count(HTML_SIMPLE)
    assert phrase == "More than 100,000 results"
