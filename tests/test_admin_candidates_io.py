import json
import os
import sys
from pathlib import Path

# Add src to sys.path for absolute imports
SRC_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "Phase 1A - Foundation",
    "Month 3 - Prototype Development",
    "EVM IoT Application",
    "src",
)
SRC_PATH = os.path.abspath(SRC_PATH)
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from ui import admin_panel


def test_save_and_load_candidates(tmp_path, monkeypatch):
    # Use a temporary file for candidates.json
    temp_file = tmp_path / "candidates.json"

    def _fake_candidates_path():
        return temp_file

    monkeypatch.setattr(admin_panel, "candidates_path", _fake_candidates_path)

    items = [
        {
            "party": "Party X",
            "candidate": "Alice",
            "symbol": "X",
            "image_path": "",
            "logo_path": "",
            "enabled": True,
        },
        {
            "party": "Party Y",
            "candidate": "Bob",
            "symbol": "Y",
            "image_path": "",
            "logo_path": "",
            "enabled": False,
        },
    ]

    admin_panel.save_candidates(items)

    # Assert file written and content matches structure
    assert temp_file.exists()
    data = json.loads(temp_file.read_text(encoding="utf-8"))
    assert "candidates" in data
    assert len(data["candidates"]) == 2
    assert data["candidates"][0]["party"] == "Party X"
    assert data["candidates"][1]["candidate"] == "Bob"

    # Load back via module function
    loaded = admin_panel.load_candidates()
    assert isinstance(loaded, list)
    assert len(loaded) == 2
    assert loaded[0]["party"] == "Party X"
    assert loaded[1]["candidate"] == "Bob"
