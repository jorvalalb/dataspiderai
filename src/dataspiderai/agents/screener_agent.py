"""
screener_agent.py – Iterate Finviz screener pages, apply optional filters
and delegate each ticker to `data_agent.scrape_company()`.
"""

from __future__ import annotations

import asyncio
import time
import urllib.parse
import json
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from dataspiderai.utils.logger import setup_logger
from dataspiderai.utils.agents_utils import extract_with_llm
from dataspiderai.agents.data_agent import scrape_company
from dataspiderai.utils.catalogs import (
    EXCHANGE_FILTERS,
    INDEX_FILTERS,
    SECTOR_FILTERS,
    make_industry_code,
    make_country_code,
)

logger = setup_logger()

ROW_STEP = 20  # tickers per screener page

# ═════════════════════ URL helpers ═════════════════════
def _build_base_url(filters: Optional[List[str]]) -> str:
    """
    Build page‑1 URL with optional Finviz filter codes.

    • No filters → https://finviz.com/screener.ashx?v=111  
    • With filters → https://finviz.com/screener.ashx?v=111&ft=4&f=code1,code2
    """
    if not filters:
        return "https://finviz.com/screener.ashx?v=111"
    encoded = urllib.parse.quote(",".join(filters), safe=",_")
    return f"https://finviz.com/screener.ashx?v=111&ft=4&f={encoded}"


def _page_url(page: int, filters: Optional[List[str]]) -> str:
    """Return the screener URL for the given page (1-based)."""
    if page == 1:
        return _build_base_url(filters)
    offset = (page - 1) * ROW_STEP + 1
    return f"{_build_base_url(filters)}&r={offset}"


# ═════════════════════ HTML fetch ═════════════════════
async def _fetch_html(url: str, engine: str) -> str:
    """Fetch and return full HTML for the given URL using Playwright."""
    logger.info("  [Screener] → GET %s", url)
    async with async_playwright() as pw:
        browser = await getattr(pw, engine).launch(headless=False)
        page = await browser.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=60_000)
        await asyncio.sleep(2)
        html = await page.content()
        await browser.close()
    logger.debug("  [Screener] ← %d bytes", len(html))
    return html


async def _extract_tickers(html: str) -> List[str]:
    """
    Use an LLM to extract all visible ticker symbols from a Finviz screener table.
    Returns a list of uppercase ticker strings.
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="screener_table") or ""
    snippet = str(table)
    prompt = (
        "Below is HTML from a Finviz screener table. "
        "Extract ALL ticker symbols visible in its body rows and return ONLY "
        "a JSON array of strings.\n\n"
        f"```html\n{snippet}\n```"
    )
    raw = await extract_with_llm(snippet, prompt)
    try:
        parsed = json.loads(raw)
        return [t.upper() for t in parsed if isinstance(t, str)]
    except json.JSONDecodeError:
        logger.warning("  [Screener] ticker JSON parse failed")
        return []


# ═════════════════════ filter slugs → codes ═════════════════════
def _translate_filters(
    exch: Optional[str],
    idx: Optional[str],
    sector: Optional[str],
    industry: Optional[str],
    country: Optional[str],
) -> List[str]:
    """Convert CLI filter slugs into the corresponding Finviz filter codes."""
    codes: List[str] = []
    if exch:
        codes.append(EXCHANGE_FILTERS[exch.lower()])
    if idx:
        codes.append(INDEX_FILTERS[idx.lower()])
    if sector:
        codes.append(SECTOR_FILTERS[sector.lower()])
    if industry:
        code = make_industry_code(industry)
        if code:
            codes.append(code)
    if country:
        code = make_country_code(country)
        if code:
            codes.append(code)
    return codes


# ═════════════════════ orchestrator ═════════════════════
async def scrape_screener_pages(
    start_page: int,
    end_page: int,
    *,
    exch: Optional[str],
    idx: Optional[str],
    sector: Optional[str],
    industry: Optional[str],
    country: Optional[str],
    do_metrics: bool,
    metrics_subset: Optional[List[str]],
    do_insiders: bool,
    do_info: bool,
    do_managers: bool,
    do_funds: bool,
    do_ratings: bool,
    do_news: bool,
    do_holdings_bd: bool,
    do_top10: bool,
    do_income: bool,
    do_balance: bool,
    do_cash: bool,
    engine: str,
) -> None:
    """
    Iterate Finviz screener pages in the given range and scrape each ticker
    according to the specified flags and filters.
    """
    filter_codes = _translate_filters(exch, idx, sector, industry, country)
    filters_str = ",".join(filter_codes) or "—"
    logger.info(
        "[Screener] Sweeping pages %d–%d | filters=%s",
        start_page, end_page, filters_str
    )

    for pg in range(start_page, end_page + 1):
        start_time = time.perf_counter()
        url = _page_url(pg, filter_codes)
        html = await _fetch_html(url, engine)

        tickers = await _extract_tickers(html)
        logger.info(
            "[Screener] Page %d: %d tickers (%.1fs)",
            pg, len(tickers), time.perf_counter() - start_time
        )

        if not tickers:
            logger.warning("[Screener] Page %d empty → stopping sweep", pg)
            break

        last_page = len(tickers) < ROW_STEP

        for sym in tickers:
            logger.info("  [Screener] ↳ Scraping %s …", sym)
            t0 = time.perf_counter()
            data: Dict[str, Any] = await scrape_company(
                symbol=sym,
                do_metrics=do_metrics,
                metrics_subset=metrics_subset,
                do_insiders=do_insiders,
                do_info=do_info,
                do_managers=do_managers,
                do_funds=do_funds,
                do_ratings=do_ratings,
                do_news=do_news,
                do_holdings_bd=do_holdings_bd,
                do_top10=do_top10,
                do_income=do_income,
                do_balance=do_balance,
                do_cash=do_cash,
                engine=engine,
            )
            logger.info(
                "  [Screener] ✓ Done %s (datasets: %s) [%.1fs]",
                sym,
                ", ".join(data.keys()) or "—",
                time.perf_counter() - t0,
            )

        if last_page:
            logger.info(
                "[Screener] Page %d had fewer than %d tickers → finished sweep",
                pg, ROW_STEP
            )
            break
