# tests/test_storage.py

import pandas as pd
import pytest
from pathlib import Path

from dataspiderai.storage.storage_handler import save_company_data

@pytest.fixture
def sample_data():
    return {
        'metrics': {'A': '1'},
        'insiders': [{'col': 'val'}],
        'info': 'desc',
        'managers': [{'name': 'M', 'percent': '1%'}],
        'funds': [{'name': 'F', 'percent': '2%'}],
        'ratings': [{'date': '2025-01-01','action':'Buy','analyst':'X','rating_change':'Up','price_target_change':'$10'}],
        'news':    [{'datetime':'2025-01-01','headline':'H','source':'S','url':'U'}],
        'income':  pd.DataFrame({'Metric':['M1'],'extracted_at':['ts']}),
        'balance': pd.DataFrame({'Metric':['M2'],'extracted_at':['ts']}),
        'cash':    pd.DataFrame({'Metric':['M3'],'extracted_at':['ts']}),
        'holdings_breakdown': [{'category':'C','percent':'5%','extracted_at':'ts'}],
        'top10_holdings':     [{'name':'N','percent':'6%','sector':'Tech','extracted_at':'ts'}],
    }

def test_save_company_data(tmp_path, sample_data):
    out = tmp_path / "data" / "SYM"
    save_company_data(
        sample_data, 'SYM',
        save_metrics=True, save_insiders=True, save_info=True,
        save_managers=True, save_funds=True, save_ratings=True,
        save_news=True, save_income=True, save_balance=True,
        save_cash=True, save_holdings_bd=True, save_top10=True,
        out_dir=str(out)
    )
    files = list(out.iterdir())
    sections = [
        'metrics','insiders','info','managers','funds',
        'ratings','news','income','balance','cash',
        'holdings_breakdown','top10_holdings',
    ]
    for sec in sections:
        assert any(f.name.startswith(f"{sec}_SYM_") for f in files)
