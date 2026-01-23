from pathlib import Path
from voteguard.app import bootstrap
from voteguard.config.env import data_dir
from voteguard.core.counting import tally


def test_tally_counts(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("VOTEGUARD_DATA", str(tmp_path))
    cv = bootstrap()
    # Cast three votes across two choices
    cv.execute("GENERAL", "Party-A", aadhaar="123456789012", voter_id="X0001")
    cv.execute("GENERAL", "Party-B", aadhaar="123456789013", voter_id="X0002")
    cv.execute("GENERAL", "Party-A", aadhaar="123456789014", voter_id="X0003")

    counts = tally(tmp_path / "ballot_ledger.json", Path("./key.key"), verify=True)

    assert "GENERAL" in counts
    assert counts["GENERAL"].get("Party-A") == 2
    assert counts["GENERAL"].get("Party-B") == 1
