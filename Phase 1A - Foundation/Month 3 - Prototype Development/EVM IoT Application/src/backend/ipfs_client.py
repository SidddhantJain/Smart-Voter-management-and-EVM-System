"""Simple IPFS HTTP client for integrating with a local IPFS node.

This module assumes an IPFS daemon is running locally (for example
via IPFS Desktop) and exposes the HTTP API on 127.0.0.1:5001.
"""

from __future__ import annotations

import pathlib
from typing import Optional

import requests


API_BASE = "http://127.0.0.1:5001/api/v0"


def add_file(path: str | pathlib.Path, pin: bool = True) -> Optional[str]:
    """Add a file from disk to IPFS and return its CID.

    Returns None if the IPFS API is not reachable or any error occurs.
    """

    p = pathlib.Path(path)
    if not p.is_file():
        return None

    params = {"pin": "true" if pin else "false"}
    try:
        with p.open("rb") as f:
            files = {"file": (p.name, f)}
            resp = requests.post(f"{API_BASE}/add", params=params, files=files, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # IPFS HTTP API returns { "Name": "..", "Hash": "<CID>", ... }
        return data.get("Hash")
    except Exception:
        return None


def add_bytes(data: bytes, name: str = "data.bin", pin: bool = True) -> Optional[str]:
    """Add an in-memory bytes object to IPFS and return its CID."""

    params = {"pin": "true" if pin else "false"}
    try:
        files = {"file": (name, data)}
        resp = requests.post(f"{API_BASE}/add", params=params, files=files, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("Hash")
    except Exception:
        return None


def cat(cid: str, timeout: int = 10) -> Optional[bytes]:
    """Fetch raw bytes for a CID from the local IPFS node.

    Returns None if the IPFS API is not reachable or any error occurs.
    """

    if not cid:
        return None
    try:
        resp = requests.post(f"{API_BASE}/cat", params={"arg": cid}, timeout=timeout)
        resp.raise_for_status()
        return resp.content
    except Exception:
        return None
