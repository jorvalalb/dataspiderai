"""
storage_handler.py — Persist scraped datasets to timestamped disk files
========================================================================

Each dataset is written into its own file so that subsequent scrapes never
overwrite previous ones.

File-name conventions
---------------------
metrics             → metrics_<TICKER>_<TIMESTAMP>.csv
insiders            → insiders_<TICKER>_<TIMESTAMP>.csv
info (description)  → info_<TICKER>_<TIMESTAMP>.txt
managers            → managers_<TICKER>_<TIMESTAMP>.csv
funds               → funds_<TICKER>_<TIMESTAMP>.csv
ratings             → ratings_<TICKER>_<TIMESTAMP>.csv
news                → news_<TICKER>_<TIMESTAMP>.csv
income statement    → income_<TICKER>_<TIMESTAMP>.csv
balance-sheet       → balance_<TICKER>_<TIMESTAMP>.csv
cash-flow           → cash_<TICKER>_<TIMESTAMP>.csv
ETF breakdown       → holdings_breakdown_<TICKER>_<TIMESTAMP>.csv
ETF top-10          → top10_holdings_<TICKER>_<TIMESTAMP>.csv
"""

from __future__ import annotations

import os
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

    Parameters
    ----------
    data : dict
        The aggregated scrape results.
    symbol : str
        Ticker symbol (used in the file names).
    out_dir : str, default "."
        Destination folder; created on demand.
    """
    _makedirs(out_dir)
    ts = _timestamp()

    # ───────── snapshot metrics ─────────
    if save_metrics and "metrics" in data:
        rows = [{"metric": k, "value": v} for k, v in data["metrics"].items()]
        pd.DataFrame(rows).to_csv(f"{out_dir}/metrics_{symbol}_{ts}.csv", index=False)

    # ───────── insider trades ───────────
    if save_insiders and "insiders" in data:
        pd.DataFrame(data["insiders"]).to_csv(
            f"{out_dir}/insiders_{symbol}_{ts}.csv", index=False
        )

    # ───────── company profile text ─────
    if save_info and "info" in data:
        with open(f"{out_dir}/info_{symbol}_{ts}.txt", "w", encoding="utf-8") as fh:
            fh.write(data["info"])

    # ───────── institutional holders ────
    if save_managers and "managers" in data:
        pd.DataFrame(data["managers"]).to_csv(
            f"{out_dir}/managers_{symbol}_{ts}.csv", index=False
        )

    if save_funds and "funds" in data:
        pd.DataFrame(data["funds"]).to_csv(
            f"{out_dir}/funds_{symbol}_{ts}.csv", index=False
        )

    # ───────── analyst ratings ──────────
    if save_ratings and "ratings" in data:
        pd.DataFrame(data["ratings"]).to_csv(
            f"{out_dir}/ratings_{symbol}_{ts}.csv", index=False
        )

    # ───────── headline news ────────────
    if save_news and "news" in data:
        pd.DataFrame(data["news"]).to_csv(
            f"{out_dir}/news_{symbol}_{ts}.csv", index=False
        )

    # ───────── financial statements ─────
    if save_income and "income" in data:
        pd.DataFrame(data["income"]).to_csv(
            f"{out_dir}/income_{symbol}_{ts}.csv", index=False
        )

    if save_balance and "balance" in data:
        pd.DataFrame(data["balance"]).to_csv(
            f"{out_dir}/balance_{symbol}_{ts}.csv", index=False
        )

    if save_cash and "cash" in data:
        pd.DataFrame(data["cash"]).to_csv(
            f"{out_dir}/cash_{symbol}_{ts}.csv", index=False
        )

    # ───────── ETF-specific datasets ────
    if save_holdings_bd and "holdings_breakdown" in data:
        pd.DataFrame(data["holdings_breakdown"]).to_csv(
            f"{out_dir}/holdings_breakdown_{symbol}_{ts}.csv",
            index=False,
        )

    if save_top10 and "top10_holdings" in data:
        pd.DataFrame(data["top10_holdings"]).to_csv(
            f"{out_dir}/top10_holdings_{symbol}_{ts}.csv",
            index=False,
        )
