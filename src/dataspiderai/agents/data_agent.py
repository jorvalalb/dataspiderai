"""
data_agent.py – Scrape Finviz datasets with granular logging, automatic
scroll-centering and ETF holdings support
===============================================================================

"""

from __future__ import annotations

import asyncio
import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from bs4 import BeautifulSoup, Tag
from playwright.async_api import async_playwright, Error as PWError, TimeoutError as PWTimeout

from dataspiderai.config import URL_TEMPLATE
from dataspiderai.utils.logger import setup_logger
from dataspiderai.utils.agents_utils import extract_with_llm
from dataspiderai.storage.storage_handler import save_company_data

logger = setup_logger()

# ═════════════════════════════ LLM helpers ══════════════════════════════════
async def _gpt_json(snippet: str, prompt: str) -> Optional[Any]:
    """Return the JSON decoded result of an LLM extraction prompt."""
    if not snippet.strip():
        return None
    try:
        txt = await extract_with_llm(snippet, prompt)
        return json.loads(txt)
    except Exception:
        return None


# ---------- Generic two-column “name + %” table (Managers / Funds) ----------
async def extract_ownership_table(
    snippet: str,
    label: str = "ownership",
) -> Optional[List[Dict[str, str]]]:
    """Return [{'name': 'BlackRock', 'percent': '8.31 %'}, …]."""
    if not snippet.strip():
        return None
    prompt = (
        f"Two-column table of {label} (name + %). Extract EVERY row and return "
        "ONLY a JSON array with keys name and percent.\n\n```html\n"
        + snippet + "\n```"
    )
    return await _gpt_json(snippet, prompt)


# ---------- Snapshot metrics ----------
async def extract_metrics(html: str) -> Optional[Dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    snippet = str(soup.find("table", class_="snapshot-table2") or "")
    prompt = (
        "Finviz snapshot metrics table – extract EVERY metric/value pair and "
        "return ONLY a JSON object.\n\n```html\n" + snippet + "\n```"
    )
    return await _gpt_json(snippet, prompt)


# ---------- Insiders ----------
async def extract_insiders(html: str) -> Optional[List[Dict[str, str]]]:
    soup = BeautifulSoup(html, "html.parser")
    snippet = str(soup.find("table", attrs={"class": re.compile(r"\bbody-table\b")}) or "")
    prompt = (
        "Finviz insiders table – extract ALL visible rows and return ONLY a "
        "JSON array.\n\n```html\n" + snippet + "\n```"
    )
    return await _gpt_json(snippet, prompt)


# ---------- Company profile ----------
async def extract_company_info(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")
    snippet = str(soup.find("div", class_="quote_profile-bio") or "")
    if not snippet.strip():
        return None
    prompt = (
        "Below is a <div class='quote_profile-bio'> from Finviz. "
        "Return ONLY its plain-text contents (no extra words).\n\n```html\n"
        + snippet + "\n```"
    )
    return (await extract_with_llm(snippet, prompt)).strip() or None


# ---------- Analyst ratings ----------
async def extract_ratings(html: str) -> Optional[List[Dict[str, str]]]:
    soup = BeautifulSoup(html, "html.parser")
    snippet = str(soup.find("table", class_="js-table-ratings") or "")
    prompt = (
        "Finviz analyst-ratings table – extract ALL visible rows and return "
        "ONLY a JSON array with keys: date, action, analyst, rating_change, "
        "price_target_change.\n\n```html\n" + snippet + "\n```"
    )
    return await _gpt_json(snippet, prompt)


# ---------- Headline news ----------
async def extract_news(html: str) -> Optional[List[Dict[str, str]]]:
    soup = BeautifulSoup(html, "html.parser")
    snippet = str(soup.find("table", id="news-table") or "")
    prompt = (
        "Finviz headline-news table – extract EVERY visible row and return ONLY "
        "a JSON array with keys datetime, headline, source, url.\n\n```html\n"
        + snippet + "\n```"
    )
    return await _gpt_json(snippet, prompt)


# ---------- ETF widgets ----------
async def extract_holdings_breakdown(html: str) -> Optional[List[Dict[str, str]]]:
    """Return [{'category': 'Tech', 'percent': '6.5%'}, …]."""
    soup = BeautifulSoup(html, "html.parser")
    snippet = str(soup.select_one("div[data-testid^='etf-holdings-bd-']") or "")
    prompt = (
        "Finviz ETF *Holdings Breakdown* widget – extract EVERY category with "
        "its percentage and return ONLY a JSON array with keys "
        "`category` and `percent`.\n\n```html\n" + snippet + "\n```"
    )
    return await _gpt_json(snippet, prompt)


async def extract_top10_holdings(html: str) -> Optional[List[Dict[str, str]]]:
    """Return [{'name': 'Apple Inc', 'percent': '20.03 %', 'sector': 'Tech'}, …]."""
    soup = BeautifulSoup(html, "html.parser")
    snippet = str(soup.select_one("div[data-testid^='etf-holdings-tt-table']") or "")
    prompt = (
        "Finviz ETF *Top 10 Holdings* table – extract EVERY row and return ONLY "
        "a JSON array with keys name, percent, sector.\n\n```html\n"
        + snippet + "\n```"
    )
    return await _gpt_json(snippet, prompt)


# ═════════════════════ Large financial tables ═════════════════════
def _bs_statement_to_df(html: str | None) -> Optional[pd.DataFrame]:
    """Convert the large statements table to a DataFrame."""
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    tbl: Tag | None = soup.find("table", {"data-testid": "quote-statements-table"})
    if not tbl:
        return None
    for svg in tbl.select("svg"):
        svg.decompose()  # remove miniature charts

    rows: list[list[str]] = []
    for tr in tbl.find_all("tr"):
        tds = tr.find_all("td")
        if not tds:
            continue
        cleaned = [td.get_text(" ", strip=True) for i, td in enumerate(tds) if i != 1]
        if len(cleaned) > 2:
            rows.append(cleaned)
    if not rows:
        return None

    header, *body = rows
    header[0] = "Metric"
    df = pd.DataFrame(body, columns=header)
    df.insert(1, "extracted_at", datetime.now().isoformat())
    return df


# ═════════════════════ Playwright helpers ════════════════════════
async def _dismiss_cookie_banner(page) -> None:
    """Dismiss common cookie banners."""
    deadline = asyncio.get_event_loop().time() + 10
    while asyncio.get_event_loop().time() < deadline:
        try:
            btn = page.locator(
                "button:has-text('AGREE'), button:has-text('ACCEPT'), button:has-text('OK')"
            ).first
            if await btn.is_visible():
                await btn.click(force=True, timeout=800)
                return
        except PWTimeout:
            pass
        await asyncio.sleep(0.4)


async def _safe_click(btn):
    """Click an element; fall back to JS if Playwright fails."""
    await btn.scroll_into_view_if_needed()
    try:
        await btn.click(force=True, timeout=8_000)
    except (PWTimeout, PWError):
        if handle := await btn.element_handle():
            await handle.evaluate("(el)=>el.click()")


async def _center(page, selector: str) -> None:
    """Scroll element into view (center)."""
    try:
        loc = page.locator(selector).first
        await page.wait_for_selector(selector, timeout=4_000)
        await loc.evaluate("el => el.scrollIntoView({block:'center'})")
        await asyncio.sleep(0.25)
    except PWTimeout:
        pass


async def _ensure_yoy_toggles(page) -> bool:
    """Activate YoY Growth toggles once per page."""
    for txt in ("YoY Growth", "YoY Growth %"):
        try:
            btn = page.locator(f"button:has-text('{txt}')").first
            await page.wait_for_selector(f"button:has-text('{txt}')", timeout=8_000)
        except PWTimeout:
            return False
        if "border-blue-400" not in (await btn.get_attribute("class") or ""):
            await _safe_click(btn)
            await asyncio.sleep(0.2)
    return True


async def _scrape_fin_table(page, tab_text: str) -> Optional[str]:
    """Switch tab inside the statements widget and return full HTML."""
    try:
        await _safe_click(page.locator(f"#statements .tab-link:has-text('{tab_text}')").first)
        await page.wait_for_selector(
            f"#statements a.tab-link.font-bold:has-text('{tab_text}')", timeout=10_000
        )
        await _center(page, "#statements")
        await asyncio.sleep(1.0)
        return await page.content()
    except (PWTimeout, PWError):
        return None


# ═════════════════════ Managers / Funds widget ═══════════════════
async def fetch_ownership_htmls(
    page,
    need_managers: bool,
    need_funds: bool
) -> Tuple[Optional[str], Optional[str]]:
    managers_html = funds_html = None
    if not (need_managers or need_funds):
        return None, None

    widget = page.locator("div.managers-and-funds")
    if not await widget.is_visible():
        return None, None

    await _center(page, "div.managers-and-funds")

    if need_funds:
        try:
            await _safe_click(widget.locator("button:has-text('Funds')").first)
            await page.wait_for_selector("div.managers-and-funds table tbody tr", timeout=5_000)
            table = await page.query_selector("div.managers-and-funds table")
            if table:
                funds_html = await table.inner_html()
        except (PWTimeout, PWError):
            pass

    if need_managers:
        try:
            await _safe_click(widget.locator("button:has-text('Managers')").first)
            await page.wait_for_selector("div.managers-and-funds table tbody tr", timeout=5_000)
            table = await page.query_selector("div.managers-and-funds table")
            if table:
                managers_html = await table.inner_html()
        except (PWTimeout, PWError):
            pass

    return managers_html, funds_html


# ═════════════════════ Persistence helpers ══════════════════════
def _save_partial(symbol: str, data: Dict[str, Any], section: str) -> None:
    """Persist only the requested section for the given symbol."""
    flags = {sec: sec == section for sec in (
        "metrics", "insiders", "managers", "funds", "ratings", "news",
        "income", "balance", "cash", "holdings_breakdown", "top10_holdings",
    )}
    save_company_data(
        data=data,
        symbol=symbol,
        out_dir=f"data/{symbol}",
        save_metrics     = flags["metrics"],
        save_insiders    = flags["insiders"],
        save_managers    = flags["managers"],
        save_funds       = flags["funds"],
        save_ratings     = flags["ratings"],
        save_news        = flags["news"],
        save_income      = flags["income"],
        save_balance     = flags["balance"],
        save_cash        = flags["cash"],
        save_holdings_bd = flags["holdings_breakdown"],
        save_top10       = flags["top10_holdings"],
    )
    logger.info("✓ %s – %s saved", symbol, section)


def _announce(sym: str, what: str):
    logger.info("↳ %s – scraping %s …", sym, what)


def _skip(sym: str, what: str):
    logger.info("ℹ %s – %s not found", sym, what)


# ═════════════════════ Main orchestrator ═════════════════════════
async def scrape_company(
    symbol: str,
    *,
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
    do_income: bool = False,
    do_balance: bool = False,
    do_cash: bool = False,
    engine: str = "firefox",
) -> Dict[str, Any]:
    """Scrape all requested datasets for a single ticker symbol."""
    data: Dict[str, Any] = {}

    async with async_playwright() as pw:
        browser = await getattr(pw, engine).launch(headless=False)
        page = await browser.new_page()
        await page.goto(
            URL_TEMPLATE.format(ticker=symbol),
            wait_until="domcontentloaded",
            timeout=60_000,
        )
        await _dismiss_cookie_banner(page)
        base_html = await page.content()

        # ---- snapshot metrics ------------------------------------------------
        if do_metrics:
            await _center(page, "table.snapshot-table2")
            _announce(symbol, "metrics")
            metrics = await extract_metrics(base_html)
            if metrics:
                if metrics_subset:
                    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
                    keep = {norm(m) for m in metrics_subset}
                    metrics = {k: v for k, v in metrics.items() if norm(k) in keep}
                metrics["extracted_at"] = datetime.now().isoformat()
                data["metrics"] = metrics
                _save_partial(symbol, data, "metrics")
            else:
                _skip(symbol, "metrics")

        # ---- insiders --------------------------------------------------------
        if do_insiders:
            await _center(page, "table.body-table")
            _announce(symbol, "insiders")
            rows = await extract_insiders(base_html)
            if rows:
                data["insiders"] = rows
                _save_partial(symbol, data, "insiders")
            else:
                _skip(symbol, "insiders")

        # ---- company profile -------------------------------------------------
        if do_info:
            await _center(page, "div.quote_profile-bio")
            _announce(symbol, "profile info")
            info = await extract_company_info(base_html)
            if info:
                data["info"] = info
            else:
                _skip(symbol, "profile info")

        # ---- analyst ratings -------------------------------------------------
        if do_ratings:
            await _center(page, "table.js-table-ratings")
            _announce(symbol, "ratings")
            rows = await extract_ratings(base_html)
            if rows:
                data["ratings"] = rows
                _save_partial(symbol, data, "ratings")
            else:
                _skip(symbol, "ratings")

        # ---- headline news ---------------------------------------------------
        if do_news:
            await _center(page, "#news-table")
            _announce(symbol, "news")
            rows = await extract_news(base_html)
            if rows:
                data["news"] = rows
                _save_partial(symbol, data, "news")
            else:
                _skip(symbol, "news")

        # ---- ETF widgets -----------------------------------------------------
        if do_holdings_bd:
            await _center(page, "div[data-testid^='etf-holdings-bd-']")
            _announce(symbol, "ETF holdings breakdown")
            rows = await extract_holdings_breakdown(base_html)
            if rows:
                data["holdings_breakdown"] = rows
                _save_partial(symbol, data, "holdings_breakdown")
            else:
                _skip(symbol, "holdings breakdown")

        if do_top10:
            await _center(page, "div[data-testid^='etf-holdings-tt-table']")
            _announce(symbol, "ETF top-10 holdings")
            rows = await extract_top10_holdings(base_html)
            if rows:
                data["top10_holdings"] = rows
                _save_partial(symbol, data, "top10_holdings")
            else:
                _skip(symbol, "top-10 holdings")

        # ---- financial statements -------------------------------------------
        if any([do_income, do_balance, do_cash]):
            if await _ensure_yoy_toggles(page):
                if do_income:
                    _announce(symbol, "income statement")
                    df = _bs_statement_to_df(await _scrape_fin_table(page, "Income Statement"))
                    if df is not None:
                        data["income"] = df
                        _save_partial(symbol, data, "income")
                    else:
                        _skip(symbol, "income")

                if do_balance:
                    _announce(symbol, "balance sheet")
                    df = _bs_statement_to_df(await _scrape_fin_table(page, "Balance Sheet"))
                    if df is not None:
                        data["balance"] = df
                        _save_partial(symbol, data, "balance")
                    else:
                        _skip(symbol, "balance")

                if do_cash:
                    _announce(symbol, "cash flow")
                    df = _bs_statement_to_df(await _scrape_fin_table(page, "Cash Flow"))
                    if df is not None:
                        data["cash"] = df
                        _save_partial(symbol, data, "cash")
                    else:
                        _skip(symbol, "cash")
            else:
                _skip(symbol, "financial statements (YoY toggles)")

        # ---- ownership widget ------------------------------------------------
        if do_managers or do_funds:
            _announce(symbol, "ownership (managers / funds)")
            mgr_html, fund_html = await fetch_ownership_htmls(page, do_managers, do_funds)

            if do_funds:
                rows = await extract_ownership_table(fund_html or "", "funds")
                if rows:
                    data["funds"] = rows
                    _save_partial(symbol, data, "funds")
                else:
                    _skip(symbol, "funds")

            if do_managers:
                rows = await extract_ownership_table(mgr_html or "", "managers")
                if rows:
                    data["managers"] = rows
                    _save_partial(symbol, data, "managers")
                else:
                    _skip(symbol, "managers")

        await browser.close()

    if data.get("info"):
        save_company_data(
            data=data,
            symbol=symbol,
            out_dir=f"data/{symbol}",
            save_metrics=False,
            save_insiders=False,
            save_managers=False,
            save_funds=False,
            save_ratings=False,
            save_news=False,
            save_income=False,
            save_balance=False,
            save_cash=False,
            save_holdings_bd=False,
            save_top10=False,
        )

    return data
