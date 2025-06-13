"""
config.py — Centralised constants & environment variables
=========================================================

"""

from __future__ import annotations

import os
from typing import Final

from dotenv import load_dotenv, find_dotenv

# ═════════════════════════ env file ═════════════════════════════════════════
# This call is harmless if no .env exists; the library just returns quietly.
load_dotenv(find_dotenv())

# ═══════════════════════ public constants ═══════════════════════════════════
OPENAI_API_KEY: Final[str | None] = os.getenv("OPENAI_API_KEY")
TEST_URL:       Final[str | None] = os.getenv("TEST_URL")

#: Finviz quote page template – pass ``ticker`` keyword argument.
URL_TEMPLATE:   Final[str] = "https://finviz.com/quote.ashx?t={ticker}&ty=c&p=d&b=1"
