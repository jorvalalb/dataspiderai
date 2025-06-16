import subprocess
import sys
import pytest

@pytest.mark.parametrize("args, expect", [
    (["-h"], "usage: dataspiderai"),
    (["--filters"], "SCREENER FILTER SLUGS"),
    (["AAPL", "--info"], "This is a sample"),  # stub your own sample
])
def test_cli_help_and_filters(tmp_path, monkeypatch, args, expect):
    # monkeypatch actual data_agent.scrape_company to print a known info
    monkeypatch.setenv("PYTHONPATH", str(tmp_path))
    res = subprocess.run([sys.executable, "-m", "dataspiderai"] + args,
                         capture_output=True, text=True)
    assert expect in res.stdout
