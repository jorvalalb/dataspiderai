# tests/test_logger.py
import io, logging
import pytest
from dataspiderai.utils.logger import setup_logger

def test_setup_logger_idempotent(tmp_path):
    logger = logging.getLogger("dataspiderai")
    logger.handlers.clear()
    logging.getLogger().handlers.clear()
    logger.propagate = False

    l1 = setup_logger()
    l2 = setup_logger()
    assert l1 is l2

    # Redirige el StreamHandler a un StringIO
    stream = io.StringIO()
    for h in logger.handlers:
        if isinstance(h, logging.StreamHandler):
            h.stream = stream

    logger.info("Test message")
    assert "dataspiderai - INFO - Test message" in stream.getvalue()

def test_file_handler_rotation(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    logger = logging.getLogger("dataspiderai")
    logger.handlers.clear()
    logging.getLogger().handlers.clear()
    logger.propagate = False

    logger = setup_logger()
    from logging.handlers import RotatingFileHandler
    fh = next(h for h in logger.handlers if isinstance(h, RotatingFileHandler))

    assert fh.maxBytes == 5 * 1024 * 1024
    assert fh.backupCount == 3

    logger.info("Hello file")
    log_file = tmp_path / "dataspiderai.log"
    assert log_file.exists()
    assert "Hello file" in log_file.read_text()
