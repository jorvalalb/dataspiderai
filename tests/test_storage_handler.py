import os
import pandas as pd
import tempfile
from storage_handler import save_company_data

def make_sample_data():
    return {
        "metrics": {"pe": "15", "pb": "1.5"},
        "insiders": [{"name": "John Doe", "date": "2025-01-01"}],
        "info": "This is a sample company.",
        "managers": [{"name": "BlackRock", "percent": "5%"}],
        "funds": [{"name": "Vanguard", "percent": "4%"}],
        "ratings": [{"date": "2025-01-02", "action": "Upgrade", "analyst": "Foo", "rating_change": "+", "price_target_change": "+1"}],
        "news": [{"datetime": "2025-01-03", "headline": "Test", "source": "Site", "url": "http://"}],
        "income": pd.DataFrame([["Revenue", "100"]], columns=["Metric", "2025"]),
        "balance": pd.DataFrame([["Assets", "200"]], columns=["Metric", "2025"]),
        "cash": pd.DataFrame([["CF", "50"]], columns=["Metric", "2025"]),
        "holdings_breakdown": [{"category": "Tech", "percent": "60%"}],
        "top10_holdings": [{"name": "AAPL", "percent": "20%", "sector": "Tech"}],
    }

def test_all_files_created(tmp_path):
    data = make_sample_data()
    save_company_data(
        data, "TST",
        save_metrics=True, save_insiders=True, save_info=True,
        save_managers=True, save_funds=True, save_ratings=True,
        save_news=True, save_income=True, save_balance=True,
        save_cash=True, save_holdings_bd=True, save_top10=True,
        out_dir=str(tmp_path),
    )
    files = sorted(os.listdir(tmp_path))
    # Expect exactly 11 files
    assert len(files) == 11
    # Check some filenames
    assert any(f.startswith("metrics_TST_") for f in files)
    assert any(f.startswith("info_TST_") and f.endswith(".txt") for f in files)
    assert any(f.startswith("holdings_breakdown_TST_") for f in files)
