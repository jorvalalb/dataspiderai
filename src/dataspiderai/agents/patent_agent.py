"""
patent_agent.py — Retrieve Google Patents result-count information
==================================================================

"""

from __future__ import annotations

import asyncio
import re
from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup
from playwright.async_api import (
    async_playwright,
    TimeoutError as PWTimeout,
)

from dataspiderai.utils.logger import setup_logger
from dataspiderai.utils.agents_utils import extract_with_llm

logger = setup_logger()

# ═════════════════════════ HTML fetcher (Playwright) ═════════════════════
async def fetch_patents_html(
    query: str,
    start_date: Optional[str],
    end_date: Optional[str],
    engine: str = "firefox",
) -> str:
    """
    Return the HTML of a Google Patents results page.

    Parameters
    ----------
    query : str
        Assignee / keyword string already URL-encoded (spaces → “+”).
    start_date, end_date : str | None
        If both are provided (YYYY-MM-DD), the *Filing date* range
        is applied via the side drawer.
    engine : str
        Playwright browser engine name.

    Notes
    -----
    • Waits for the DOM to be loaded; adds brief sleeps for dynamic
      content to settle.
    • When dates are supplied, explicitly waits for the refreshed
      counter (`div#count`) before returning.
    """
    url = f"https://patents.google.com/?assignee={query}&oq={query}"
    logger.info("[Patents] GET %s", url)

    async with async_playwright() as pw:
        browser = await getattr(pw, engine).launch(headless=False)
        page = await browser.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=60_000)
        await asyncio.sleep(2)  # allow JS widgets to finish

        if start_date and end_date:
            logger.info("[Patents] Applying filing-date filter %s → %s",
                        start_date, end_date)
            await page.click("span#compactQuery")
            await page.click("dropdown-menu[label='Date'] iron-icon")
            await page.click("div.item:has-text('Filing')")
            await page.fill("input#after",  start_date)
            await page.fill("input#before", end_date)
            await page.press("input#before", "Enter")

            try:
                await page.wait_for_selector("div#count", timeout=60_000)
            except PWTimeout:
                logger.warning("[Patents] Timeout waiting for updated count")
            await asyncio.sleep(1)

        html = await page.content()
        await browser.close()
    return html

# ═════════════════════════ LLM extractor ════════════════════════════════
async def extract_patent_count(html: str) -> str:
    """
    Extract the *exact* visible phrase that shows the number of results.

    The phrase may include qualifiers such as “More than”, “About”, etc.
    The function removes any accidental Markdown fences returned by the
    LLM but otherwise preserves the text verbatim.
    """
    soup = BeautifulSoup(html, "html.parser")
    count_div = soup.find("div", id="count")
    snippet = str(count_div) if count_div else html[:600]

    prompt = (
        "Below is HTML from Google Patents that contains the total results "
        "counter (e.g. “More than 100 000 results”).\n"
        "Return ONLY the visible phrase — do not add or remove words.\n\n"
        f"```html\n{snippet}\n```"
    )
    raw = await extract_with_llm(snippet, prompt)
    text = raw.strip()

    fence_match = re.search(r"```(?:\w+)?\s*([\s\S]*?)```", text)
    if fence_match:
        text = fence_match.group(1).strip()
    return text

# ═════════════════════════ Orchestrator helper ═══════════════════════════
async def scrape_patents(
    query: str,
    start_date: Optional[str],
    end_date: Optional[str],
    engine: str = "firefox",
) -> dict:
    """
    Execute the full pipeline and return a structured result.

    Returns
    -------
    {
        "count_phrase": str,   # literal phrase (may include qualifiers)
        "count": int | None,   # parsed integer if possible
        "scraped_at": ISO-8601 timestamp
    }
    """
    html = await fetch_patents_html(query, start_date, end_date, engine)
    phrase = await extract_patent_count(html)

    num_match = re.search(r"[\d\.,]+", phrase.replace(" ", ""))
    count_int = (
        int(num_match.group(0).replace(".", "").replace(",", ""))
        if num_match else None
    )

    if not count_int:
        phrase = "No results found"
        count_int = 0

    logger.info("[Patents] %s → %s", query, phrase)
    return {
        "count_phrase": phrase,
        "count": count_int,
        "scraped_at": datetime.now().isoformat(),
    }
