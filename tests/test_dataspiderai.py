"""
tests/test_dataspiderai.py — Pytest suite for DataSpiderAI
===========================================================

"""

import os
import re
import pytest
import importlib
import pandas as pd
import sys
import asyncio
from datetime import datetime

from dataspiderai.config import URL_TEMPLATE, OPENAI_API_KEY
from dataspiderai.utils.catalogs import (
    make_industry_code, make_country_code,
    INDUSTRY_CODES, COUNTRY_CODES,
    EXCHANGE_FILTERS, EXCH_SLUGS,
    INDEX_FILTERS, IDX_SLUGS,
    SECTOR_FILTERS, SECTOR_SLUGS,
    INDUSTRY_SLUGS, COUNTRY_SLUGS,
)
from dataspiderai.utils.logger import setup_logger
from dataspiderai.cli import (
    _cli_token, _pretty_patent_phrase,
    _build_parser, parse_args, run_pipeline
)
from dataspiderai.agents.screener_agent import (
    _build_base_url, _page_url,
    _translate_filters, ROW_STEP
)
from dataspiderai.storage.storage_handler import (
    save_company_data, _timestamp
)
from dataspiderai.agents.data_agent import _bs_statement_to_df


def reload_config():
    return importlib.reload(__import__('dataspiderai.config', fromlist=['']))


def test_config_url_template():
    assert isinstance(URL_TEMPLATE, str)
    assert '{ticker}' in URL_TEMPLATE


def test_openai_api_key_env(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'test_key')
    config = reload_config()
    assert config.OPENAI_API_KEY == 'test_key'


def test_make_industry_and_country_code():
    sample_industry = next(iter(INDUSTRY_CODES))
    assert make_industry_code(sample_industry) == INDUSTRY_CODES[sample_industry]
    assert make_industry_code('nonexistent') is None

    sample_country = next(iter(COUNTRY_CODES))
    assert make_country_code(sample_country) == COUNTRY_CODES[sample_country]
    assert make_country_code('foo') is None


def test_logger_setup_returns_named_logger(caplog):
    logger = setup_logger()
    assert logger.name == 'dataspiderai'
    caplog.set_level('INFO')
    logger.info('test-message')
    assert 'test-message' in caplog.text


def test_cli_token():
    assert _cli_token('P/E') == 'p/e'
    assert _cli_token('EPS (ttm)') == 'epsttm'
    assert _cli_token('SMA20') == 'sma20'


def test_pretty_patent_phrase():
    assert _pretty_patent_phrase('More than 100 results') == 'More than 100'
    assert _pretty_patent_phrase('about 200 resultados') == 'Above 200'
    assert _pretty_patent_phrase('"123 results"') == '123'


def test_build_parser_contains_expected_args():
    parser = _build_parser()
    actions = [a.dest for a in parser._actions]
    assert 'metrics' in actions and 'insiders' in actions


def test_translate_filters_and_urls():
    assert _translate_filters('nasd', None, None, None, None) == ['exch_nasd']
    assert _translate_filters(None, 'sp500', None, None, None) == ['idx_sp500']
    codes = _translate_filters('nasd', 'sp500', 'basicmaterials', None, 'usa')
    for code in ('exch_nasd', 'idx_sp500', 'sec_basicmaterials', 'geo_usa'):
        assert code in codes

    base = _build_base_url(None)
    assert 'v=111' in base and 'f=' not in base
    filters = ['a','b']
    base2 = _build_base_url(filters)
    assert 'f=a,b' in base2

    page1 = _page_url(1, filters)
    assert page1 == base2
    page2 = _page_url(2, filters)
    offset = (2 - 1) * ROW_STEP + 1
    assert f'r={offset}' in page2


def test_translate_filters_invalid_raises():
    with pytest.raises(KeyError):
        _translate_filters('invalid', None, None, None, None)


def test_timestamp_format():
    ts = _timestamp()
    assert re.match(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}", ts)


def test_save_company_data(tmp_path):
    data = {
        'metrics': {'A': '1'},
        'insiders': [{'col': 'val'}],
        'info': 'desc',
        'managers': [{'name': 'M', 'percent': '1%'}],
        'funds': [{'name': 'F', 'percent': '2%'}],
        'ratings': [{'date': '2025-01-01', 'action': 'Buy', 'analyst': 'X', 'rating_change': 'Up', 'price_target_change': '$10'}],
        'news': [{'datetime': '2025-01-01', 'headline': 'H', 'source': 'S', 'url': 'U'}],
        'income': pd.DataFrame({'Metric': ['M1'], 'TTM': ['10'], 'extracted_at': ['ts']}),
        'balance': pd.DataFrame({'Metric': ['M2'], 'FY 2024': ['20'], 'extracted_at': ['ts']}),
        'cash': pd.DataFrame({'Metric': ['M3'], 'TTM': ['30'], 'extracted_at': ['ts']}),
        'holdings_breakdown': [{'category': 'C', 'percent': '5%', 'extracted_at': 'ts'}],
        'top10_holdings': [{'name': 'N', 'percent': '6%', 'sector': 'Tech', 'extracted_at': 'ts'}],
    }
    out_dir = tmp_path / 'data' / 'SYM'
    save_company_data(
        data, 'SYM',
        save_metrics=True, save_insiders=True, save_info=True,
        save_managers=True, save_funds=True, save_ratings=True,
        save_news=True, save_income=True, save_balance=True,
        save_cash=True, save_holdings_bd=True, save_top10=True,
        out_dir=str(out_dir)
    )
    files = list(out_dir.iterdir())
    expected_sections = [
        'metrics', 'insiders', 'info', 'managers', 'funds',
        'ratings', 'news', 'income', 'balance', 'cash',
        'holdings_breakdown', 'top10_holdings',
    ]
    for sec in expected_sections:
        assert any(f.name.startswith(f'{sec}_SYM_') for f in files)


def test_bs_statement_to_df_with_valid_html():
    html = (
        '<table data-testid="quote-statements-table">'
        '<tr><td>Metric</td><td>X</td><td>FY 2024</td><td>FY 2023</td></tr>'
        '<tr><td>Rev</td><td></td><td>100</td><td>90</td></tr>'
        '</table>'
    )
    df = _bs_statement_to_df(html)
    assert df is not None
    assert 'Metric' in df.columns and 'FY 2024' in df.columns
    assert df.loc[0, 'Metric'] == 'Rev'


def test_bs_statement_to_df_with_invalid_html():
    assert _bs_statement_to_df(None) is None
    assert _bs_statement_to_df('<div>No table here</div>') is None


def test_cli_no_args_exit(monkeypatch, capsys):
    monkeypatch.setattr(sys, 'argv', ['dataspiderai'])
    args = parse_args()
    with pytest.raises(SystemExit):
        asyncio.run(run_pipeline(args))
    captured = capsys.readouterr()
    assert 'Error: provide at least one ticker or use --screener' in captured.err


def test_cli_patents_bad_usage(monkeypatch, capsys):
    monkeypatch.setattr(sys, 'argv', ['dataspiderai', '--patents', 'A', 'B'])
    args = parse_args()
    with pytest.raises(SystemExit):
        asyncio.run(run_pipeline(args))
    captured = capsys.readouterr()
    assert 'Usage:' in captured.err


def test_catalogs_slugs_sync():
    assert set(EXCHANGE_FILTERS.keys()) == set(EXCH_SLUGS)
    assert set(INDEX_FILTERS.keys()) == set(IDX_SLUGS)
    assert set(SECTOR_FILTERS.keys()) == set(SECTOR_SLUGS)
    assert set(INDUSTRY_CODES.keys()) == set(INDUSTRY_SLUGS)
    assert set(COUNTRY_CODES.keys()) == set(COUNTRY_SLUGS)
