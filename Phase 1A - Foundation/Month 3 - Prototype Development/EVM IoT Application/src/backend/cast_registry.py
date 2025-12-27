"""
Simple cast registry to prevent double voting.
Stores pairs of (aadhaar_id, voter_id) in a JSON file.
"""
import os
import json
from pathlib import Path
from typing import Tuple


REGISTRY_FILE = Path(__file__).resolve().parents[3] / "cast_registry.json"


def _load() -> set[Tuple[str, str]]:
    if not REGISTRY_FILE.exists():
        return set()
    try:
        data = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
        return set((entry[0], entry[1]) for entry in data)
    except Exception:
        return set()


def _save(entries: set[Tuple[str, str]]) -> None:
    payload = list([a, v] for (a, v) in entries)
    REGISTRY_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def has_cast(aadhaar_id: str, voter_id: str) -> bool:
    entries = _load()
    return (aadhaar_id, voter_id) in entries


def mark_cast(aadhaar_id: str, voter_id: str) -> None:
    entries = _load()
    entries.add((aadhaar_id, voter_id))
    _save(entries)
