# 🚀📈 **dataspiderai – AI-assisted Financial & Patent Web Scraper**

<div align="center">

[![GitHub Stars](https://img.shields.io/github/stars/your-org/dataspiderai?style=social)](https://github.com/your-org/dataspiderai/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/your-org/dataspiderai?style=social)](https://github.com/your-org/dataspiderai/network/members)

[![PyPI version](https://badge.fury.io/py/dataspiderai.svg)](https://pypi.org/project/dataspiderai/)
[![Python Versions](https://img.shields.io/pypi/pyversions/dataspiderai)](https://pypi.org/project/dataspiderai/)
[![Downloads](https://static.pepy.tech/badge/dataspiderai/month)](https://pepy.tech/project/dataspiderai)

[![License](https://img.shields.io/github/license/your-org/dataspiderai)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

</div>

**dataspiderai** is an *async*, multi-agent toolkit that fuses **Playwright** automation with **GPT-4o** post-processing to scrape:

- Comprehensive **Finviz** datasets (fundamentals, ownership, ETF holdings, statements, news…)
- **Google Patents** hit counts with optional filing-date filters

Open-source, headless-by-default and fully incremental — every dataset is saved the very moment it is scraped so no work is lost.

[**✨ Latest version: v1.0.0**](CHANGELOG.md) – now with one-flag patent searching, live console output for company profiles and 200+ screener filter slugs.

---

## 🧐 Why dataspiderai ?

| #   | Reason                   | Detail                                                                 |
|-----|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| **1** | **Agentic Architecture** | *Physical* Playwright agents click & scroll; *LLM* agents convert raw HTML to JSON. |
| **2** | **Finance-First**         | Purpose-built for Finviz: snapshot ratios, insider trades, institutional ownership, YoY statements, ETF widgets. |
| **3** | **Patent Counter**        | One-liner `--patents "query" [start end]` returns exact Google Patents hit phrase in 30 s. |
| **4** | **Incremental Saves**     | Each section flushes to `data/<TICKER>/…csv` instantly — resilient to crashes. |
| **5** | **Ultra-Flexible Screener** | Iterate any page range, combine 200+ filter slugs, and decide *exactly* which datasets to fetch. |
| **6** | **Zero Server-Side Fee**  | Runs locally; you only need an `OPENAI_API_KEY`.                       |
| **7** | **Cross-Platform**        | Tested on Linux, Windows & macOS (Python ≥ 3.10).                      |
| **8** | **Verbose Logging**       | One-line log per action; warnings when a table is missing, never crashes the whole run. |

---

## 🚀 Quick Start (30 s)

```bash
# 1. install package + playwright browsers
pip install dataspiderai
playwright install

# 2. snapshot metrics + insiders for Apple
dataspiderai AAPL --metrics --insiders
```

Console:
```
2025-06-14 12:00:00 - dataspiderai - INFO - ↳ AAPL – scraping metrics …
✓ AAPL – metrics saved
✓ AAPL – insiders saved
```

---

## 🛠️ Installation

```bash
# stable
pip install dataspiderai

# pre-release
pip install dataspiderai --pre
```

If Playwright complains about missing browsers:

```bash
python -m playwright install --with-deps chromium firefox webkit
```

---

## 🔐 .env Configuration

Create a file named `.env` in the root of your project:

```bash
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

Replace `your_openai_api_key_here` with your actual key. This is required for all LLM-based extractions.

---

## 🏛️ Agent Architecture

```text
┌────────────────────────────────────────────────────────────────────┐
│                          CLI / Entry Point                        │
│            (dataspiderai / dataspiderai.py – module cli.py)       │
└────────────────────────────────────────────────────────────────────┘
          │
          ▼                                ┌────────────────────────┐
┌────────────────────────┐                 │  Screener Agent    │
│  Main Orchestrator│◀───────────────▶│ (screener_agent.py)   │
│  run_pipeline()        │  <bandera --screener>                 │
└────────────────────────┘                 └────────────────────────┘
          │
          │ without --screener
          ▼
┌────────────────────────┐                 ┌────────────────────────┐
│  Data Agent        │◀───────────────▶│  Storage Handler       │
│  data_agent.scrape_    │  se invoca      │  (storage_handler.py) │
│  company()             │  para cada      └────────────────────────┘
└────────────────────────┘  ticker/dataset
          │
          ▼
┌────────────────────────┐
│  Playwright (navegación)│
│  + BeautifulSoup        │
└────────────────────────┘
          │
          ▼
┌────────────────────────┐
│  Agentes LLM (extract_ │
│    _metrics, _insiders,│
│    extract_with_llm…)   │
└────────────────────────┘

CLI `--patents` → `patent_agent.scrape_patents()`
                       │
                       ▼
                 `fetch_patents_html()`
                       │
                       ▼
              `extract_patent_count()`
```

---

## 📑 Full CLI Reference

| Category    | Flag(s)                                                                 | Notes                                |
|-------------|-------------------------------------------------------------------------|--------------------------------------|
| **Basic**   | `symbols…`                                                              | One or more ticker symbols (`AAPL MSFT …`). |
| **Patents** | `--patents "QUERY"`<br>`--patents "QUERY" START END`                    | **Exclusive**. Returns Google Patents hit count phrase.<br>Dates in `YYYY-MM-DD`. |
| **Screener**| `--screener [START [END]]`, `-pg …`                                     | Iterate Finviz screener pages (20 tickers/page). Omit → all pages. |
| **Filters** | `--exch`, `--idx`, `--sector`, `--industry`, `--country`, `--filters`  | 200+ slugs — list them all with `--filters`. |
| **Datasets**| `--metrics [TOKENS…]`, `--insiders`, `--info`, `--managers`, `--funds`, `--ratings`, `--news`, `--holdings-bd`, `--top10`, `--income`, `--balance`, `--cash` | Flags are additive. Omit all ⇒ *full sweep*. |
| **Browser** | `--browser chromium|firefox|webkit`                                      | Default `firefox`.                   |
| **Help**    | `flag --help`                                                           | Contextual sub-help (e.g. `--metrics --help`). |

---

## 📊 Datasets Explained

| Flag               | File(s)                          | Description                                                        |
|--------------------|----------------------------------|--------------------------------------------------------------------|
| `--metrics`        | `metrics_<SYM>_<ts>.csv`         | 100+ snapshot ratios/indicators. Supports token subset (`p/e peg sma200`). |
| `--insiders`       | `insiders_…csv`                  | Insider trades w/ relationship & SEC Form 4 link.                  |
| `--managers`       | `managers_…csv`                  | Top asset-manager holders (% of shares).                           |
| `--funds`          | `funds_…csv`                     | Top funds/ETFs holders.                                            |
| `--ratings`        | `ratings_…csv`                   | Date, analyst, rating & price-target changes.                     |
| `--news`           | `news_…csv`                      | Timestamp, headline, source, URL.                                  |
| `--income`         | `income_…csv`                    | Annual Income Statement (YoY %).                                   |
| `--balance`        | `balance_…csv`                   | Annual Balance Sheet (YoY %).                                      |
| `--cash`           | `cash_…csv`                      | Annual Cash-flow Statement (YoY %).                                |
| `--holdings-bd`    | `holdings_breakdown_…csv`        | ETF category vs % of assets.                                       |
| `--top10`          | `top10_holdings_…csv`            | ETF top-10 holdings (name, % weight, sector).                      |
| `--info`           | `info_…txt` (and printed)        | Plain-text business description.                                   |

---

## 🔍 Usage Recipes

### 1 — Single ticker, custom metrics + profile
```bash
dataspiderai GOOG --metrics p/e peg sma50 sma200 --info
```

### 2 — ETF widgets only
```bash
dataspiderai QQQ --holdings-bd --top10
```

### 3 — Headline-news only
```bash
dataspiderai TSLA --news
```

### 4 — Patents (date filtered)
```bash
dataspiderai --patents "quantum dot display" 2024-01-01 2024-12-31
# 🔎  'quantum dot display': About 87 results
```

### 5 — Screener: all European NASDAQ stocks, Income+Balance
```bash
dataspiderai --screener --exch nasd --country europe --income --balance
```

### 6 — Screener pages 5–8, semiconductor industry, full sweep
```bash
dataspiderai --screener 5 8 --industry semiconductors
```

---

## 🔧 Advanced Playwright Tweaks

```bash
# run headed Firefox for debugging
dataspiderai AAPL --metrics --browser firefox

# change default pause & viewport via env vars
export DATASPIDERAI_PLAYWRIGHT_PAUSE=1.5
export DATASPIDERAI_VIEWPORT="1440x900"
```

---

## 🗂️ Project Structure

```
src/dataspiderai/
├─ cli.py
├─ agents/
│  ├─ data_agent.py
│  ├─ screener_agent.py
│  └─ patent_agent.py
├─ utils/
│  ├─ agents_utils.py
│  ├─ catalogs.py
│  └─ logger.py
└─ storage/
   └─ storage_handler.py
```

---

## 📥 Output Example

```
data/AAPL/
├─ metrics_AAPL_2025-06-14_12-03-27.csv
└─ news_AAPL_2025-06-14_12-03-28.csv
```

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📜 License & Citation

MIT © 2025 Jorge Valverde Albelda

```bibtex
@software{valverde2025dataspiderai,
  author  = {Jorge Valverde Albelda},
  title   = {dataspiderai: AI-assisted Finviz & Google Patents Scraper},
  year    = {2025},
  url     = {https://github.com/jorgevalverdealbe/dataspiderai},
  version = {1.0.0}
}
```

Happy scraping! 🕸️🤖
