# tests/test_agent_utils.py
import pytest
from dataspiderai.utils.agents_utils import extract_with_llm

class DummyReply:
    def __init__(self, content):
        self.content = content

class DummyLLM:
    def __init__(self, responses):
        self._responses = responses
        self._idx = 0

    async def ainvoke(self, prompt):
        content = self._responses[min(self._idx, len(self._responses)-1)]
        self._idx += 1
        return DummyReply(content)

@pytest.mark.asyncio
async def test_extract_with_llm_prefers_fenced_json(monkeypatch):
    responses = ["intro\n```json\n{\"a\":1,\"b\":2}\n``` outro"]
    monkeypatch.setattr(
        "dataspiderai.utils.agents_utils.ChatOpenAI",
        lambda model: DummyLLM(responses)
    )
    out = await extract_with_llm("<html/>", "p")
    assert out == '{"a":1,"b":2}'

@pytest.mark.asyncio
async def test_extract_with_llm_fallback_to_first_json_fragment(monkeypatch):
    responses = ["some text {\"x\":10,\"y\":20} more"]
    monkeypatch.setattr(
        "dataspiderai.utils.agents_utils.ChatOpenAI",
        lambda model: DummyLLM(responses)
    )
    out = await extract_with_llm("", "")
    assert out == '{"x":10,"y":20}'

@pytest.mark.asyncio
async def test_extract_with_llm_returns_trimmed(monkeypatch):
    responses = ["   plain text result   "]
    monkeypatch.setattr(
        "dataspiderai.utils.agents_utils.ChatOpenAI",
        lambda model: DummyLLM(responses)
    )
    out = await extract_with_llm("", "")
    assert out == "plain text result"
