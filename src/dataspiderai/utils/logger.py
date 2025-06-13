"""
logger.py — Package-wide logger factory
=======================================

"""

from __future__ import annotations

import logging
from typing import Final

# ═════════════════════════ constants ════════════════════════════════════════
_LOGGER_NAME:   Final[str] = "dataspiderai"
_LOG_LEVEL:     Final[int] = logging.INFO
_FMT:           Final[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


# ═════════════════════════ factory helper ═══════════════════════════════════
def setup_logger() -> logging.Logger:
    """
    Return a ``logging.Logger`` pre-configured for console output.

    The logger is created only once; repeated calls simply fetch the existing
    instance so that every module in the package shares the same handlers.
    """
    logger = logging.getLogger(_LOGGER_NAME)
    if logger.handlers:            # already initialised → early exit
        return logger

    logger.setLevel(_LOG_LEVEL)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(_LOG_LEVEL)
    console_handler.setFormatter(logging.Formatter(_FMT))

    logger.addHandler(console_handler)
    return logger
