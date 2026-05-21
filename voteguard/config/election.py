from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

from .env import data_dir


DEFAULT_ELECTION_SETTINGS: Dict[str, Any] = {
    "election_type": "Vidhan Sabha",
    "constituency": "",
    "state": "",
    "server_host": "127.0.0.1",
    "server_port": 8785,
    "approval_host": "127.0.0.1",
    "approval_port": 8765,
}


def election_settings_path() -> Path:
    return data_dir() / "election_settings.json"


def load_election_settings() -> Dict[str, Any]:
    path = election_settings_path()
    if not path.exists():
        return deepcopy(DEFAULT_ELECTION_SETTINGS)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return deepcopy(DEFAULT_ELECTION_SETTINGS)
        merged = deepcopy(DEFAULT_ELECTION_SETTINGS)
        merged.update(raw)
        return merged
    except Exception:
        return deepcopy(DEFAULT_ELECTION_SETTINGS)


def save_election_settings(settings: Dict[str, Any]) -> Path:
    path = election_settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = deepcopy(DEFAULT_ELECTION_SETTINGS)
    payload.update(settings)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
