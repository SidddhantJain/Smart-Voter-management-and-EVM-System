from __future__ import annotations

import os
from pathlib import Path


def data_dir() -> Path:
    return Path(os.getenv("VOTEGUARD_DATA", "./data")).resolve()


def key_path() -> Path:
    return Path(os.getenv("FERNET_KEY_PATH", "./key.key")).resolve()


def enable_camera() -> bool:
    return os.getenv("ENABLE_CAMERA", "0") == "1"


def enable_ml() -> bool:
    return os.getenv("ENABLE_ML", "0") == "1"


def model_dir() -> Path:
    # Default to Phase 1A - Foundation/models if present, else ./models
    default_dir = Path("./Phase 1A - Foundation/models").resolve()
    if default_dir.exists():
        return default_dir
    return Path(os.getenv("ML_MODEL_DIR", "./models")).resolve()


def overlays_enabled() -> bool:
    """Global toggle for camera/UI overlays (text boxes, labels)."""
    return os.getenv("VOTEGUARD_OVERLAYS", "1") == "1"
