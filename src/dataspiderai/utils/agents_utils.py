"""
agents_utils.py — Shared helpers for physical & LLM sub-agents
==============================================================

"""

from __future__ import annotations

import asyncio
import re
from typing import Final

from playwright.async_api import async_playwright
from langchain_openai import ChatOpenAI

# ═════════════════════════ constants ════════════════════════════════════════
_DEFAULT_ENGINE:      Final[str]   = "firefox"
_DEFAULT_MODEL:       Final[str]   = "gpt-4o"
_DEFAULT_SLEEP:       Final[float] = 2.0
_NAV_TIMEOUT_MS:      Final[int]   = 60_000


# ═════════════════════════ Playwright helper ════════════════════════════════
async def fetch_html(
    url: str,
    *,
    engine: str = _DEFAULT_ENGINE,
    headless: bool = False,
    pause: float = _DEFAULT_SLEEP,
) -> str:
    """
    Launch the selected Playwright *engine*, load *url* and return the page
    HTML once **DOMContentLoaded** fires.

    Parameters
    ----------
    url : str
        Target URL.
    engine : {"chromium", "firefox", "webkit"}, default "firefox"
        Playwright browser to use.
    headless : bool, default False
        Whether to run the browser in headless mode.
    pause : float, default 2 s
        Seconds to wait after DOM load to allow lazy resources to settle.
    """
    async with async_playwright() as pw:
        browser = await getattr(pw, engine).launch(headless=headless)
        page    = await browser.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=_NAV_TIMEOUT_MS)
        await asyncio.sleep(pause)
        html = await page.content()
        await browser.close()
    return html


# ═════════════════════════ OpenAI-LLM helper ════════════════════════════════
async def extract_with_llm(
    html_snippet: str,
    prompt: str,
    *,
    model: str = _DEFAULT_MODEL,
) -> str:
    """
    Feed *html_snippet* and *prompt* to the specified OpenAI chat model and
    return its textual response.  If the reply includes a fenced ```json``` block
    that block is extracted; otherwise the entire reply is returned after
    trimming.

    The helper also tries a simple fallback — returning the first well-formed
    {...} JSON fragment it can spot.
    """
    llm   = ChatOpenAI(model=model)
    reply = await llm.ainvoke(prompt)
    text  = reply.content or ""

    fenced = re.search(r"```json\s*([\s\S]*?)```", text, flags=re.I)
    if fenced:
        return fenced.group(1).strip()

    start, end = text.find("{"), text.rfind("}")
    if 0 <= start < end:
        return text[start : end + 1].strip()

    return text.strip()
