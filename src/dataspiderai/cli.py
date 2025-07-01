"""
cli.py – Command-line entry-point for *dataspiderai*
===================================================

"""

from __future__ import annotations

import argparse
import asyncio
import os
import re
import sys
import textwrap
from typing import List, Optional

from dataspiderai.utils.logger import setup_logger
from dataspiderai.utils.catalogs import (
    METRICS_DOCS, INSIDERS_COLS, MANAGERS_COLS, FUNDS_COLS, RATINGS_COLS,
    NEWS_COLS, INCOME_COLS, BALANCE_COLS, CASH_COLS,
    EXCH_SLUGS, IDX_SLUGS, SECTOR_SLUGS, INDUSTRY_SLUGS, COUNTRY_SLUGS,
)
from dataspiderai.agents.data_agent     import scrape_company
from dataspiderai.agents.screener_agent import scrape_screener_pages
from dataspiderai.agents.patent_agent   import scrape_patents

logger = setup_logger()

# ═════════════════════════ general helpers ═════════════════════════
def _cli_token(header: str) -> str:
    """Return a canonical token for a Finviz header (lower-snake, no symbols)."""
    return re.sub(r"[^\w/]", "", header.lower())


def _pretty_patent_phrase(phrase: str) -> str:
    """
    Clean and localise the Google-Patents counter phrase.
    Removes trailing “results/resultados” and translates qualifiers.
    """
    text = phrase.strip(' "“”').strip()
    text = re.sub(r"\s*(results?|resultados?)\s*$", "", text, flags=re.I)
    match = re.match(r"(?i)(more than|about)\s+(.*)", text)
    if match:
        qual = "More than" if match.group(1).lower() == "more than" else "Above"
        text = f"{qual} {match.group(2)}"
    return text

# ═════════════════════════ dataset inline-help ═════════════════════
def _show_metrics_help() -> None:
    print("\nMETRICS DATASET")
    print("----------------")
    print('Example:\n  dataspiderai AAPL --metrics p/e volume sma200\n')
    print(textwrap.fill(
        "Scrapes the Finviz “snapshot” table with valuation, performance and "
        "technical ratios. Call `--metrics` alone for the full table or pass "
        "tokens to limit the scrape.", width=80))
    width = max(len(_cli_token(k)) for k in METRICS_DOCS)
    print("\nAvailable tokens:\n")
    for k, desc in METRICS_DOCS.items():
        print(f"  {_cli_token(k).ljust(width)}  ({desc})")
    sys.exit(0)


def _show_simple_help(title: str, flag: str, cols: List[str], blurb: str) -> None:
    print(f"\n{title.upper()} DATASET")
    print("-" * (len(title) + 8))
    print(f'Example:\n  dataspiderai AAPL {flag}\n')
    print(textwrap.fill(blurb, width=80))
    print("\nColumns:\n")
    for col in cols:
        print(f"  {col}")
    sys.exit(0)


def _show_insiders_help()    -> None: _show_simple_help("Insiders",    "--insiders", INSIDERS_COLS,
    "Scrapes the Finviz insider-trading table (directors, officers, 10-percent owners).")
def _show_managers_help()    -> None: _show_simple_help("Managers",    "--managers", MANAGERS_COLS,
    "Scrapes the Institutional-Ownership tab in its “Managers” view.")
def _show_funds_help()       -> None: _show_simple_help("Funds",       "--funds",    FUNDS_COLS,
    "Scrapes the Institutional-Ownership tab in its “Funds” view.")
def _show_ratings_help()     -> None: _show_simple_help("Ratings",     "--ratings",  RATINGS_COLS,
    "Scrapes the analyst-ratings table (date, action, analyst, change).")
def _show_news_help()        -> None: _show_simple_help("News",        "--news",     NEWS_COLS,
    "Scrapes the headline-news feed on a Finviz quote page.")
def _show_income_help()      -> None: _show_simple_help("Income",      "--income",   INCOME_COLS,
    "Scrapes the *Income Statement* table (annual YoY view).")
def _show_balance_help()     -> None: _show_simple_help("Balance",     "--balance",  BALANCE_COLS,
    "Scrapes the *Balance Sheet* table (annual YoY view).")
def _show_cash_help()        -> None: _show_simple_help("Cash-Flow",   "--cash",     CASH_COLS,
    "Scrapes the *Cash Flow* statement (annual YoY view).")
def _show_holdings_bd_help() -> None: _show_simple_help("Holdings-BD", "--holdings-bd",
    ["category", "percent"], "Scrapes the ETF *Holdings Breakdown* widget.")
def _show_top10_help()       -> None: _show_simple_help("Top-10",      "--top10",
    ["name", "percent", "sector"], "Scrapes the ETF *Top-10 Holdings* table.")

# ═════════════════════════ screener filter help ═══════════════════
def _show_filters_help() -> None:
    wrap = lambda s: textwrap.fill(s, width=80)
    print("\nSCREENER FILTER SLUGS")
    print("----------------------")
    print(wrap("Use these slugs with --exch --idx --sector --industry --country "
               "to pre-filter the Finviz screener sweep.\n"))
    print("Exchanges :", ", ".join(sorted(EXCH_SLUGS)))
    print("Indices   :", ", ".join(sorted(IDX_SLUGS)))
    print("Sectors   :", ", ".join(sorted(SECTOR_SLUGS)))
    print(f"Industries ({len(INDUSTRY_SLUGS)}): "
          + ", ".join(sorted(INDUSTRY_SLUGS)[:12]) + " …")
    print("Countries :", ", ".join(sorted(COUNTRY_SLUGS)))
    sys.exit(0)

# Map flag → sub-help function
_HELP_MAP = {
    "--metrics": _show_metrics_help, "--insiders": _show_insiders_help,
    "--managers": _show_managers_help, "--funds": _show_funds_help,
    "--ratings": _show_ratings_help, "--news": _show_news_help,
    "--income": _show_income_help, "--balance": _show_balance_help,
    "--cash": _show_cash_help, "--holdings-bd": _show_holdings_bd_help,
    "--top10": _show_top10_help, "--filters": _show_filters_help,
}

def _maybe_handle_subhelp() -> None:
    """Show flag-specific help if user requested `flag --help`."""
    argv = sys.argv[1:]
    for flag, func in _HELP_MAP.items():
        if flag in argv:
            idx = argv.index(flag)
            if any(tok in ("-h", "--help") for tok in argv[idx + 1:]):
                func()
_maybe_handle_subhelp()

# ═════════════════════════ argparse boilerplate ═══════════════════
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dataspiderai",
        description="Scrape Finviz & Google-Patents datasets via AI agents.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    # Output format
    p.add_argument("--output", "-o",
                   choices=["csv", "parquet", "json"],
                   default="csv",
                   help="Output format for saved datasets (default: csv).")

    # Patents (exclusive)
    p.add_argument("--patents", nargs="+", metavar="ARG",
                   help='Query in quotes; optionally add START END (YYYY-MM-DD).')

    # Finviz / Screener
    p.add_argument("symbols", nargs="*", help="Ticker symbols (e.g. AAPL MSFT)")
    p.add_argument("--screener", "-pg", nargs="*", metavar=("START", "END"),
                   help="Screener mode: 0 args→all pages, 1→single, 2→range.")

    p.add_argument("--exch", choices=sorted(EXCH_SLUGS))
    p.add_argument("--idx",  choices=sorted(IDX_SLUGS))
    p.add_argument("--sector", choices=sorted(SECTOR_SLUGS))
    p.add_argument("--industry", choices=INDUSTRY_SLUGS)
    p.add_argument("--country",  choices=COUNTRY_SLUGS)
    p.add_argument("--filters",  action="store_true", help="Show filter slugs")

    # Dataset flags
    p.add_argument("--metrics", nargs="*", metavar="METRIC")
    p.add_argument("--insiders", action="store_true")
    p.add_argument("--info",     action="store_true")
    p.add_argument("--managers", action="store_true")
    p.add_argument("--funds",    action="store_true")
    p.add_argument("--ratings",  action="store_true")
    p.add_argument("--news",     action="store_true")
    p.add_argument("--holdings-bd", action="store_true")
    p.add_argument("--top10",       action="store_true")
    p.add_argument("--income",   action="store_true")
    p.add_argument("--balance",  action="store_true")
    p.add_argument("--cash",     action="store_true")

    p.add_argument("--browser", choices=["chromium", "firefox", "webkit"],
                   default="firefox")
    return p


def parse_args() -> argparse.Namespace:
    args = _build_parser().parse_args()
    if args.filters:
        _show_filters_help()
    return args

# ═════════════════════════ patents helper ═════════════════════════
async def _run_patents(
    query_raw: str,
    start: Optional[str],
    end: Optional[str],
    engine: str
) -> None:
    query_enc = query_raw.replace(" ", "+")
    res = await scrape_patents(query_enc, start, end, engine=engine)
    if res and res["count_phrase"]:
        print(f"\n🔎  '{query_raw}': {_pretty_patent_phrase(res['count_phrase'])} results\n")
    else:
        print("⚠ Patents scraping failed.", file=sys.stderr)

# ═════════════════════════ pipeline runner ════════════════════════
async def run_pipeline(args: argparse.Namespace) -> None:
    # make output format available to storage
    os.environ["DATASPIDERAI_OUTPUT_FORMAT"] = args.output

    # ---------- PATENTS (exclusive) ----------
    if args.patents is not None:
        if len(args.patents) not in (1, 3):
            print("Usage:\n  --patents \"query\"\n  --patents \"query\" START END",
                  file=sys.stderr); sys.exit(1)
        query_raw = args.patents[0]
        start = end = None
        if len(args.patents) == 3:
            start, end = args.patents[1:3]
        await _run_patents(query_raw, start, end, engine=args.browser)
        return

    # ---------- Screener branch ----------
    if args.screener is not None:
        if len(args.screener) == 0:
            start_pg, end_pg = 1, 503
        elif len(args.screener) == 1:
            start_pg = end_pg = int(args.screener[0])
        elif len(args.screener) == 2:
            start_pg, end_pg = map(int, args.screener)
        else:
            raise ValueError("--screener expects 0, 1 or 2 integers")

        metrics_flag   = args.metrics is not None
        metrics_subset = [m.lower() for m in args.metrics] if metrics_flag and args.metrics else None
        full_sweep = not any([
            metrics_flag, args.insiders, args.info, args.managers, args.funds,
            args.ratings, args.news, args.holdings_bd, args.top10,
            args.income,  args.balance, args.cash,
        ])

        await scrape_screener_pages(
            start_page=start_pg, end_page=end_pg,
            exch=args.exch, idx=args.idx, sector=args.sector,
            industry=args.industry, country=args.country,
            do_metrics   = metrics_flag or full_sweep,
            metrics_subset = metrics_subset,
            do_insiders  = args.insiders or full_sweep,
            do_info      = args.info,
            do_managers  = args.managers or full_sweep,
            do_funds     = args.funds    or full_sweep,
            do_ratings   = args.ratings  or full_sweep,
            do_news      = args.news,
            do_holdings_bd = args.holdings_bd or full_sweep,
            do_top10       = args.top10       or full_sweep,
            do_income    = args.income  or full_sweep,
            do_balance   = args.balance or full_sweep,
            do_cash      = args.cash    or full_sweep,
            engine       = args.browser,
        )
        return

    # ---------- Single-ticker branch ----------
    if not args.symbols:
        print("Error: provide at least one ticker or use --screener\n",
              file=sys.stderr)
        _build_parser().print_usage(sys.stderr); sys.exit(1)

    metrics_flag   = args.metrics is not None
    metrics_subset = [m.lower() for m in args.metrics] if metrics_flag and args.metrics else None
    full_sweep = not any([
        metrics_flag, args.insiders, args.info, args.managers, args.funds,
        args.ratings, args.news, args.holdings_bd, args.top10,
        args.income, args.balance, args.cash,
    ])

    for raw in args.symbols:
        sym = raw.upper()
        logger.info("=== Processing %s ===", sym)

        data = await scrape_company(
            symbol=sym,
            do_metrics   = metrics_flag or full_sweep,
            metrics_subset = metrics_subset,
            do_insiders  = args.insiders or full_sweep,
            do_info      = args.info,
            do_managers  = args.managers or full_sweep,
            do_funds     = args.funds    or full_sweep,
            do_ratings   = args.ratings  or full_sweep,
            do_news      = args.news,
            do_holdings_bd = args.holdings_bd or full_sweep,
            do_top10       = args.top10       or full_sweep,
            do_income    = args.income  or full_sweep,
            do_balance   = args.balance or full_sweep,
            do_cash      = args.cash    or full_sweep,
            engine       = args.browser,
        )

        # Print company description if requested
        if args.info and data.get("info"):
            print("\n" + data["info"].strip() + "\n")

# ═════════════════════════ entry-point ════════════════════════════
def main() -> None:
    try:
        asyncio.run(run_pipeline(parse_args()))
    except KeyboardInterrupt:
        print("\n↪ Cancelación solicitada por el usuario (Ctrl-C). Saliendo…\n")

if __name__ == "__main__":
    main()
