from __future__ import annotations
import os
from pathlib import Path


def data_dir() -> Path:
    return Path(os.getenv("VOTEGUARD_DATA", "./data")).resolve()


def key_path() -> Path:
    return Path(os.getenv("FERNET_KEY_PATH", "./key.key")).resolve()
