import pytest
from dataspiderai.agents.screener_agent import _translate_filters

def test_translate_filters_all():

    codes = _translate_filters("nasd", "sp500", "technology", "semiconductors", "usa")

    assert any(c.startswith("exch_nasd") for c in codes)
    assert any(c.startswith("idx_sp500") for c in codes)

def test_translate_filters_none():
    codes = _translate_filters(None, None, None, None, None)
    assert codes == []
