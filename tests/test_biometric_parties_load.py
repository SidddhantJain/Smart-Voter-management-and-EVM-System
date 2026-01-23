import json
import os
import sys
import types
from pathlib import Path

from PyQt5.QtWidgets import QApplication, QStackedWidget

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

# Stub heavy ML module before importing biometric_capture to avoid native crashes
dummy_ml = types.ModuleType("voteguard.adapters.ml_analytics_optional")
setattr(dummy_ml, "analyze", lambda frame: [])
setattr(dummy_ml, "models_loaded", lambda: {"emotion": False, "demographics": False})
sys.modules["voteguard.adapters.ml_analytics_optional"] = dummy_ml

from ui import biometric_capture as bc


def test_load_parties_from_config(tmp_path, monkeypatch):
    # Patch cv2 to avoid opening real camera
    monkeypatch.setattr(bc, "cv2", None)

    # Prepare fake candidates.json in repo data path used by the function
    # Use the same base directory the module uses
    base = Path(bc.__file__).resolve().parents[3]
    data_dir = base / "data"
    data_dir.mkdir(exist_ok=True)
    candidates_file = data_dir / "candidates.json"
    original = None
    if candidates_file.exists():
        original = candidates_file.read_text(encoding="utf-8")

    payload = {
        "candidates": [
            {
                "party": "Party Z",
                "candidate": "Zed",
                "symbol": "Z",
                "image_path": "",
                "logo_path": "",
                "enabled": True,
            },
            {
                "party": "Hidden",
                "candidate": "Ghost",
                "symbol": "H",
                "image_path": "",
                "logo_path": "",
                "enabled": False,
            },
        ]
    }
    candidates_file.write_text(json.dumps(payload), encoding="utf-8")

    try:
        app = QApplication.instance() or QApplication([])
        widget = QStackedWidget()
        screen = bc.BiometricCaptureScreen(widget)
        parties = screen._load_parties_from_config()
        assert isinstance(parties, list)
        # Only enabled entries should appear
        assert len(parties) == 1
        assert parties[0]["name"] == "Party Z"
        assert parties[0]["candidate_name"] == "Zed"
    finally:
        # Restore original file if present
        if original is not None:
            candidates_file.write_text(original, encoding="utf-8")
        else:
            try:
                os.remove(str(candidates_file))
            except Exception:
                pass
