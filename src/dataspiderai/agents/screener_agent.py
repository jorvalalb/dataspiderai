"""
screener_agent.py – Iterate Finviz screener pages, apply optional filters
and delegate each ticker to `data_agent.scrape_company()`.

"""

from __future__ import annotations

import asyncio
import time
import urllib.parse
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

ROW_STEP = 20             # tickers per screener page

# ═════════════════════ URL helpers ═════════════════════
def _build_base_url(filters: Optional[List[str]]) -> str:
    """
    Build page-1 URL with optional Finviz filter codes.

    • No filters → https://finviz.com/screener.ashx?v=111  
    • With filters → https://finviz.com/screener.ashx?v=111&ft=4&f=code1,code2
    """
    if not filters:
        return "https://finviz.com/screener.ashx?v=111"
    encoded = urllib.parse.quote(",".join(filters), safe=",_")
    return f"https://finviz.com/screener.ashx?v=111&ft=4&f={encoded}"


def _page_url(page: int, filters: Optional[List[str]]) -> str:
    """Return the screener URL for *page* (1-based)."""
    if page == 1:
        return _build_base_url(filters)
    offset = (page - 1) * ROW_STEP + 1
    return f"{_build_base_url(filters)}&r={offset}"

# ═════════════════════ HTML fetch ═════════════════════
async def _fetch_html(url: str, engine: str) -> str:
    """Return full HTML for *url* using the chosen Playwright engine."""
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
    """LLM-extract visible ticker symbols from a screener table."""
    soup = BeautifulSoup(html, "html.parser")
    snippet = str(soup.find("table", class_="screener_table") or "")
    prompt = (
        "Below is HTML from a Finviz screener table. "
        "Extract ALL ticker symbols visible in its body rows and return ONLY "
        "a JSON array of strings.\n\n"
        f"```html\n{snippet}\n```"
    )
    raw = await extract_with_llm(snippet, prompt)
    try:
        return [t.upper() for t in eval(raw) if isinstance(t, str)]
    except Exception:
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
    """Convert CLI filter slugs to Finviz filter codes."""
    codes: List[str] = []
    if exch:     codes.append(EXCHANGE_FILTERS[exch.lower()])
    if idx:      codes.append(INDEX_FILTERS[idx.lower()])
    if sector:   codes.append(SECTOR_FILTERS[sector.lower()])
    if industry: codes.append(make_industry_code(industry))
    if country:  codes.append(make_country_code(country))
    return [c for c in codes if c]

# ═════════════════════ orchestrator ═════════════════════
async def scrape_screener_pages(
    start_page: int,
    end_page: int,
    *,
    # filters
    exch: Optional[str],
    idx: Optional[str],
    sector: Optional[str],
    industry: Optional[str],
    country: Optional[str],
    # data-agent flags
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
    """Sweep screener pages and scrape each ticker with the supplied flags."""
    filter_codes = _translate_filters(exch, idx, sector, industry, country)
    logger.info(
        "[Screener] Sweeping pages %d–%d | filters=%s",
        start_page, end_page, ",".join(filter_codes) or "—"
    )

    for pg in range(start_page, end_page + 1):
        page_t0 = time.perf_counter()
        html = await _fetch_html(_page_url(pg, filter_codes), engine)

        tickers = await _extract_tickers(html)
        logger.info("[Screener] Page %d: %d tickers (%.1fs)",
                    pg, len(tickers), time.perf_counter() - page_t0)

        if not tickers:
            logger.warning("[Screener] Page %d empty → stopping sweep", pg)
            break
        last_page = len(tickers) < ROW_STEP

        # ── scrape each ticker ──
        for sym in tickers:
            logger.info("  [Screener] ↳ Scraping %s …", sym)
            t0 = time.perf_counter()

            data: Dict[str, Any] = await scrape_company(
                symbol=sym,
                do_metrics=do_metrics, metrics_subset=metrics_subset,
                do_insiders=do_insiders, do_info=do_info,
                do_managers=do_managers, do_funds=do_funds,
                do_ratings=do_ratings, do_news=do_news,
                do_holdings_bd=do_holdings_bd, do_top10=do_top10,
                do_income=do_income, do_balance=do_balance,
                do_cash=do_cash, engine=engine,
            )

            logger.info(
                "  [Screener] ✓ Done %s (datasets: %s) [%.1fs]",
                sym, ", ".join(data.keys()) or "—",
                time.perf_counter() - t0,
            )

        if last_page:
            logger.info("[Screener] Page %d had < %d tickers → Finished\n",
                        pg, ROW_STEP)
            break
