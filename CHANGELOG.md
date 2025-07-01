# Changelog

All notable changes to **dataspiderai** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] – 2025-07-01

### Added
- `--output` flag to select output format (csv, parquet, json).  
- Environment variable `DATASPIDERAI_OUTPUT_FORMAT` fallback for default format.  
- Support for Parquet and JSON output in `storage_handler`.  
- Enhanced README with step-by-step installation using **uv** (fast, lock-aware manager).  
- Updated `.env` documentation and installation steps.  
- New `CONTRIBUTING.md` instructions for development with **uv** venv and editable installs.  
- Contextual inline help for output formats in the CLI reference.

### Changed
- README reorganized: clarified package description, installation, and usage.  
- README now emphasizes Finviz as core functionality; patents as optional extra.  
- Updated CLI reference table to include `--output` flag.  
- Updated agent architecture diagram to match latest code.  

### Fixed
- Minor typos in documentation and code examples.  

---

## [0.1.0] – 2025-05-20

### Added
- **Core CLI** (`dataspiderai`):
  - Scrape single or multiple tickers from Finviz.
  - Support for Finviz “snapshot” metrics, insider trades, analyst ratings, headline news, and financial statements (Income, Balance Sheet, Cash Flow).
  - ETF support: holdings breakdown and top-10 holdings extraction.
  - Incremental, timestamped CSV/TXT output for each dataset.
  - Customizable subset of metrics via `--metrics` tokens.
  - `--info` flag to print the company profile text extracted from Finviz.
  - Screener mode (`--screener`), with optional filters by exchange, index, sector, industry, and country.
  - `--filters` command to list all valid screener‐slug values.
- **Google Patents integration** (`--patents`):
  - Exclusive mode: when provided, skips all Finviz scraping.
  - Accepts 1-arg (query) or 3-arg (query + start/end dates) invocation.
  - Applies “Filing date” filters via Playwright UI.
  - Extracts and prints the total results count, cleansed and localized (English → Spanish).
  - Supports multi-word assignee queries (spaces → `+` in URL).
- **Agents & Utilities**:
  - `data_agent`: multi-agent orchestration to fetch HTML, center/scroll pages, apply YOY toggles, extract tables via LLM, and save results.
  - `screener_agent`: paginated Finviz screener loop with GPT-powered ticker extraction.
  - `patent_agent`: Playwright-based patent HTML fetcher & LLM extractor for count phrases.
  - `agents_utils`: shared helpers for HTML fetching and LLM JSON extraction.
  - `storage_handler`: unified CSV/TXT persistence with per-dataset timestamping.
- **Logging & UX**:
  - Granular INFO-level logs with clear symbols (↳, ✓, ℹ) for scraping steps.
  - Ctrl-C handling for graceful exit.
  - Clean, focused console output for `--info` and `--patents` modes.
  - Main `-h/--help` no longer floods with screener slugs—use `--filters` instead.
- **Configuration & Catalog**:
  - Centralized `catalogs.py` with snapshot metric docs, table schemas, and screener‐slug mappings.
  - Argparse integration using descriptive token lists and custom inline-help for each dataset.

---

*This changelog will be updated for future releases.*
