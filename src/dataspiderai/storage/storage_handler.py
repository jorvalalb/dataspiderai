"""
storage_handler.py — Persist scraped datasets to timestamped disk files
========================================================================

Each dataset is written into its own file so that subsequent scrapes never
overwrite previous ones.

File-name conventions
---------------------
metrics             → metrics_<TICKER>_<TIMESTAMP>.<ext>
insiders            → insiders_<TICKER>_<TIMESTAMP>.<ext>
info (description)  → info_<TICKER>_<TIMESTAMP>.<txt/.json>
managers            → managers_<TICKER>_<TIMESTAMP>.<ext>
funds               → funds_<TICKER>_<TIMESTAMP>.<ext>
ratings             → ratings_<TICKER>_<TIMESTAMP>.<ext>
news                → news_<TICKER>_<TIMESTAMP>.<ext>
income statement    → income_<TICKER>_<TIMESTAMP>.<ext>
balance-sheet       → balance_<TICKER>_<TIMESTAMP>.<ext>
cash-flow           → cash_<TICKER>_<TIMESTAMP>.<ext>
ETF breakdown       → holdings_breakdown_<TICKER>_<TIMESTAMP>.<ext>
ETF top-10          → top10_holdings_<TICKER>_<TIMESTAMP>.<ext>
"""

from __future__ import annotations

import os
import json
from datetime import datetime
from typing import Any, Dict

import pandas as pd

# ═════════════════════════ helpers ════════════════════════════════════════
def _timestamp() -> str:
    """Return local time as `YYYY-MM-DD_HH-MM-SS`."""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def _makedirs(path: str) -> None:
    """`mkdir -p` helper — create folder tree if it does not exist."""
    os.makedirs(path, exist_ok=True)


# ═════════════════════════ main writer ════════════════════════════════════
def save_company_data(
    data: Dict[str, Any],
    symbol: str,
    *,
    # individual dataset switches
    save_metrics: bool,
    save_insiders: bool,
    save_info: bool = False,
    save_managers: bool = False,
    save_funds: bool = False,
    save_ratings: bool = False,
    save_news: bool = False,
    save_income: bool = False,
    save_balance: bool = False,
    save_cash: bool = False,
    save_holdings_bd: bool = False,
    save_top10: bool = False,
    out_dir: str = ".",
) -> None:
    """
    Write the requested sections of *data* to disk using the conventions
    shown in the module doc-string.

    The output format is controlled by the DATASPIDERAI_OUTPUT_FORMAT
    environment variable: 'csv' (default), 'parquet', or 'json'.
    """
    fmt = os.getenv("DATASPIDERAI_OUTPUT_FORMAT", "csv").lower()
    _makedirs(out_dir)
    ts = _timestamp()

    def _write_df(df: pd.DataFrame, prefix: str):
        base = f"{out_dir}/{prefix}_{symbol}_{ts}"
        if fmt == "parquet":
            df.to_parquet(f"{base}.parquet", index=False)
        elif fmt == "json":
            df.to_json(f"{base}.json", orient="records", date_format="iso")
        else:
            df.to_csv(f"{base}.csv", index=False)

    def _write_list(lst: list, prefix: str):
        base = f"{out_dir}/{prefix}_{symbol}_{ts}"
        if fmt == "parquet":
            pd.DataFrame(lst).to_parquet(f"{base}.parquet", index=False)
        elif fmt == "json":
            with open(f"{base}.json", "w", encoding="utf-8") as fh:
                json.dump(lst, fh, ensure_ascii=False, indent=2)
        else:
            pd.DataFrame(lst).to_csv(f"{base}.csv", index=False)

    # ───────── snapshot metrics ─────────
    if save_metrics and "metrics" in data:
        rows = [{"metric": k, "value": v} for k, v in data["metrics"].items()]
        _write_df(pd.DataFrame(rows), "metrics")

    # ───────── insider trades ───────────
    if save_insiders and "insiders" in data:
        _write_list(data["insiders"], "insiders")

    # ───────── company profile text ─────
    if save_info and "info" in data:
        base = f"{out_dir}/info_{symbol}_{ts}"
        if fmt == "json":
            with open(f"{base}.json", "w", encoding="utf-8") as fh:
                json.dump({"info": data["info"]}, fh, ensure_ascii=False, indent=2)
        else:
            with open(f"{base}.txt", "w", encoding="utf-8") as fh:
                fh.write(data["info"])

    # ───────── institutional holders ────
    if save_managers and "managers" in data:
        _write_list(data["managers"], "managers")
    if save_funds and "funds" in data:
        _write_list(data["funds"], "funds")

    # ───────── analyst ratings ──────────
    if save_ratings and "ratings" in data:
        _write_list(data["ratings"], "ratings")

    # ───────── headline news ────────────
    if save_news and "news" in data:
        _write_list(data["news"], "news")

    # ───────── financial statements ─────
    if save_income and "income" in data:
        _write_df(data["income"], "income")
    if save_balance and "balance" in data:
        _write_df(data["balance"], "balance")
    if save_cash and "cash" in data:
        _write_df(data["cash"], "cash")

    # ───────── ETF-specific datasets ────
    if save_holdings_bd and "holdings_breakdown" in data:
        _write_list(data["holdings_breakdown"], "holdings_breakdown")
    if save_top10 and "top10_holdings" in data:
        _write_list(data["top10_holdings"], "top10_holdings")
