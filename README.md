# 🚀📈 **dataspiderai – AI-assisted Financial & Patent Web Scraper**

<div align="center">

[![GitHub Stars](https://img.shields.io/github/stars/jorvalalb/dataspiderai?style=social)](https://github.com/jorvalalb/dataspiderai/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/jorvalalb/dataspiderai?style=social)](https://github.com/jorvalalb/dataspiderai/forks)

[![PyPI version](https://badge.fury.io/py/dataspiderai.svg)](https://pypi.org/project/dataspiderai/)
[![Python Versions](https://img.shields.io/pypi/pyversions/dataspiderai)](https://pypi.org/project/dataspiderai/)
[![Downloads](https://static.pepy.tech/badge/dataspiderai/month)](https://pepy.tech/project/dataspiderai)

[![License](https://img.shields.io/github/license/jorvalalb/dataspiderai)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

</div>

**dataspiderai** is an *async*, multi-agent toolkit that fuses **Playwright** browser automation with **GPT-4o** prompts to turn complex web UIs into clean, timestamped datasets. Its primary focus is:

- **Finviz** scraping: snapshot ratios, insider trades, institutional ownership, ETF widgets, financial statements, news feeds.
- **Google Patents** Patent counts from Google Patents via a single flag.

Everything is saved _incrementally_—as soon as a section is scraped, it’s flushed to disk so you never lose progress.

[**✨ Latest version: v1.0.0**](CHANGELOG.md) — now with `--output` support (csv, parquet, json), contextual help, and 200+ screener filters.

---

## 🧐 Why dataspiderai?

| #    | Reason                      | Detail                                                                 |
|------|-----------------------------|------------------------------------------------------------------------|
| **1** | **Agentic Architecture**      | *Physical* Playwright agents click & scroll; *LLM* agents convert HTML → JSON. |
| **2** | **Finance-First**             | Built for Finviz: snapshot, insiders, ownership, statements, ETFs, news. |
| **3** | **Incremental Saves**         | Each section writes immediately to `data/<TICKER>/…` — crash-resilient.  |
| **4** | **Ultra-Flexible Screener**   | Sweep any pages, combine 200+ filter slugs, pick exactly the datasets you want. |
| **5** | **Zero Server-Side Fee**      | Runs entirely locally; you only need an `OPENAI_API_KEY`.               |
| **6** | **Cross-Platform**            | Works on Linux, Windows & macOS (Python ≥ 3.12).                       |
| **7** | **Verbose Logging**           | One-line log per action; warnings on missing tables, never crashes.     |
| **8** | **Output Formats**            | Save CSV (default), Parquet or JSON via `--output` flag.               |

---

---

## 🛠️ Installation (step-by-step with `uv`)

We recommend `uv`—an extremely fast, lock-aware Python package manager and environment tool:

1. **Install `uv`**  
   ```bash
   pip install uv
   ```
   `uv` handles venv creation, dependency resolution and installs in milliseconds.

2. **Clone or install**  
   - **Clone locally**  
     ```bash
     git clone https://github.com/jorvalalb/dataspiderai.git
     cd dataspiderai
     ```
   - **Or install from PyPI**  
     ```bash
     uv pip install dataspiderai
     ```

3. **Create & activate a venv**  
   ```bash
   uv venv create dataspiderai-env
   dataspiderai-env\Scripts\activate      # Windows
   ```

4. **Install dependencies**  
   ```bash
   uv sync --active
   ```

5. **Install Playwright browsers**  
   ```bash
   python -m playwright install --with-deps chromium firefox webkit
   ```

6. **Configure your `.env`**  
   ```bash
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

7. **Verify & run**  
   ```bash
   dataspiderai --help
   ```
   or  
   ```bash
   dataspiderai AAPL --metrics --output parquet
   ```

---

## 🔐 `.env` Configuration

Create a file named `.env` in the root of your project:

```bash
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

Replace `your_openai_api_key_here` with your actual key. This is required for all LLM-based extractions.

---

## 🏛️ Agent Architecture

```text
┌────────────────────────────────────────────────────────────────────┐
│                          CLI / Entry Point                         │
│            (dataspiderai / dataspiderai.py – CLI module)           │
└────────────────────────────────────────────────────────────────────┘
          │
          ▼                                ┌────────────────────────┐
┌────────────────────────┐                 │  Screener Agent        │
│  Main Orchestrator     │◀───────────────▶│ (screener_agent.py)   │
│  run_pipeline()        │  <flag --screener>                       │
└────────────────────────┘                 └────────────────────────┘
          │
          │ without --screener
          ▼
┌────────────────────────┐                 ┌────────────────────────┐
│  Data Agent            │◀───────────────▶│  Storage Handler      │
│  data_agent.scrape_    │  invoked for    │  (storage_handler.py)  │
│  company()             │  each ticker/   └────────────────────────┘
└────────────────────────┘  dataset
          │
          ▼
┌────────────────────────┐
│ Playwright (navigation)│
│ + BeautifulSoup        │
└────────────────────────┘
          │
          ▼
┌────────────────────────┐
│  LLM Agents (extract_  │
│    _metrics, _insiders,│
│    extract_with_llm…)  │
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
| **Patents** | `--patents "QUERY"`<br>`--patents "QUERY" START END`                    | Returns Google Patents hit count phrase.<br>Dates in `YYYY-MM-DD`. |
| **Screener**| `--screener [START [END]]`, `-pg …`                                     | Sweep Finviz screener pages (20 tickers/page). Omit → all pages. |
| **Filters** | `--exch`, `--idx`, `--sector`, `--industry`, `--country`, `--filters`  | 200+ slugs — list them with `--filters`. |
| **Datasets**| `--metrics [TOKENS…]`, `--insiders`, `--info`, `--managers`, `--funds`,<br>`--ratings`, `--news`, `--holdings-bd`, `--top10`, `--income`, `--balance`, `--cash` | Flags are additive. Omit all ⇒ *full sweep*. |
| **Output**  | `--output {csv,parquet,json}`                                           | Choose file format (default: csv).   |
| **Browser** | `--browser {firefox,chromium,webkit}`                                      | Default `firefox`.                   |
| **Help**    | `flag --help`                                                           | Contextual sub-help (e.g. `--metrics --help`). |

---

## 📊 Datasets Explained

| Flag               | File(s)                          | Description                                                        |
|--------------------|----------------------------------|--------------------------------------------------------------------|
| `--metrics`        | `metrics_<SYM>_<ts>.<ext>`       | 100+ snapshot ratios/indicators. Supports token subset (`p/e sma200`). |
| `--insiders`       | `insiders_<SYM>_<ts>.<ext>`      | Insider trades with relationship & SEC Form 4 link.               |
| `--managers`       | `managers_<SYM>_<ts>.<ext>`      | Top asset-manager holders (% of shares).                          |
| `--funds`          | `funds_<SYM>_<ts>.<ext>`         | Top fund/ETF holders.                                             |
| `--ratings`        | `ratings_<SYM>_<ts>.<ext>`       | Date, analyst, rating & price-target changes.                     |
| `--news`           | `news_<SYM>_<ts>.<ext>`          | Timestamp, headline, source, URL.                                  |
| `--income`         | `income_<SYM>_<ts>.<ext>`        | Annual Income Statement (YoY %).                                   |
| `--balance`        | `balance_<SYM>_<ts>.<ext>`       | Annual Balance Sheet (YoY %).                                      |
| `--cash`           | `cash_<SYM>_<ts>.<ext>`          | Annual Cash Flow Statement (YoY %).                                |
| `--holdings-bd`    | `holdings_breakdown_<SYM>_<ts>.<ext>` | ETF category vs % of assets.                                    |
| `--top10`          | `top10_holdings_<SYM>_<ts>.<ext>`| ETF top-10 holdings (name, % weight, sector).                      |
| `--info`           | `info_<SYM>_<ts>.txt` / `.json`  | Plain-text business description (printed on console).             |

---

## 🔍 Usage Recipes

### 1 — Single ticker + custom metrics
```bash
dataspiderai GOOG --metrics p/e peg sma50 sma200
```

### 2 — ETF widgets
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

### 7 — Save as Parquet instead of CSV
```bash
dataspiderai AAPL --metrics --output parquet
```

---

## 🗂️ Project Structure

```
src/dataspiderai/
├─ config.py
├─ cli.py
├─ agents/
│  ├─ data_agent.py
│  ├─ patent_agent.py
│  └─ screener_agent.py
├─ utils/
│  ├─ agents_utils.py
│  ├─ catalogs.py
│  └─ logger.py
└─ storage/
   └─ storage_handler.py
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
  url     = {https://github.com/jorvalalb/dataspiderai},
  version = {1.0.0}
}
```

Happy scraping! 🕸️🤖
