# tests/test_utils.py
import re, os
import pytest
from pathlib import Path
from dataspiderai.storage.storage_handler import _timestamp, _makedirs

def test_timestamp_format():
    ts = _timestamp()
    assert re.match(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}", ts)

def test_makedirs(tmp_path):
    d = tmp_path / "lvl1" / "lvl2"
    assert not d.exists()
    _makedirs(str(d))
    assert d.exists()