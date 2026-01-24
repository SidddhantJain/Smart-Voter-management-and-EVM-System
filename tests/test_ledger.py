import os
from pathlib import Path

from voteguard.app import bootstrap
from voteguard.config.env import data_dir


def test_append_and_verify(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("VOTEGUARD_DATA", str(tmp_path))
    cv = bootstrap()
    r1 = cv.execute("GENERAL", "Party-A", aadhaar="123456789012", voter_id="X0001")
    r2 = cv.execute("GENERAL", "Party-B", aadhaar="123456789013", voter_id="X0002")
    assert r1.seq == 1 and r2.seq == 2
    # Verify with script logic
    from scripts.verify_ledger import verify

    assert verify(tmp_path / "ballot_ledger.json") == 0
