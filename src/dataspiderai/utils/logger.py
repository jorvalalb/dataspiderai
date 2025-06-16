"""
logger.py — Configure package-wide logging to console and file.
================================================================

"""

import logging
from logging.handlers import RotatingFileHandler
import os

_LOGGER_NAME = "dataspiderai"
_LOG_FILENAME = "dataspiderai.log"
_MAX_BYTES = 5 * 1024 * 1024
_BACKUP_COUNT = 3
_LEVEL = logging.INFO
_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def setup_logger() -> logging.Logger:
    """
    Configure and return the "dataspiderai" logger.

    - Console handler: INFO level
    - File handler: INFO level, rotating when file exceeds 5 MB,
      keeping up to 3 backups.
    """
    logger = logging.getLogger(_LOGGER_NAME)
    if logger.hasHandlers():
        return logger

    logger.setLevel(_LEVEL)

    # ─── Console handler ─────────────────────────────────────────────
    ch = logging.StreamHandler()
    ch.setLevel(_LEVEL)
    ch.setFormatter(logging.Formatter(_FORMAT))
    logger.addHandler(ch)

    # ─── File handler ────────────────────────────────────────────────
    log_path = os.path.join(os.getcwd(), _LOG_FILENAME)
    fh = RotatingFileHandler(
        filename=log_path,
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    fh.setLevel(_LEVEL)
    fh.setFormatter(logging.Formatter(_FORMAT))
    logger.addHandler(fh)

    return logger
