from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import asdict
from pathlib import Path
from typing import Tuple

from cryptography.fernet import Fernet

from ..core.domain import Vote


class HashChainedLedger:
    def __init__(self, ledger_path: Path, key_path: Path):
        self.ledger_path = ledger_path
        self.key_path = key_path
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        self._fernet = Fernet(self._load_or_create_key())
        if not self.ledger_path.exists():
            self._write_json({"header": self._header(), "records": []})

    def _header(self):
        return {
            "version": 1,
            "created_at": time.time(),
            "build_fingerprint": os.getenv("VOTEGUARD_BUILD", "dev"),
            "assurance_level": os.getenv("VOTEGUARD_ASSURANCE", "L0"),
        }

    def _load_or_create_key(self) -> bytes:
        if not self.key_path.exists():
            self.key_path.parent.mkdir(parents=True, exist_ok=True)
            self.key_path.write_bytes(Fernet.generate_key())
        return self.key_path.read_bytes()

    def _read_json(self):
        return json.loads(self.ledger_path.read_text("utf-8"))

    def _write_json(self, obj):
        tmp = self.ledger_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(obj, indent=2))
        tmp.replace(self.ledger_path)

    def append_encrypted(self, vote: Vote) -> Tuple[int, str]:
        data = self._read_json()
        records = data.get("records", [])
        seq = len(records) + 1
        prev_hash = records[-1]["record_hash"] if records else "0" * 64
        plaintext = json.dumps(
            {"vote": vote.to_public_json(), "meta": {"ts": time.time()}},
            separators=(",", ":"),
        ).encode("utf-8")
        ciphertext = self._fernet.encrypt(plaintext).decode("utf-8")
        record_hash = hashlib.sha256(
            (prev_hash + ":" + ciphertext + ":" + str(seq)).encode("utf-8")
        ).hexdigest()
        records.append(
            {
                "seq": seq,
                "prev_hash": prev_hash,
                "ciphertext": ciphertext,
                "record_hash": record_hash,
            }
        )
        data["records"] = records
        self._write_json(data)
        return seq, record_hash


class JsonCastRegistry:
    def __init__(self, path: Path):
        self.path = path
        if not self.path.exists():
            self._write_json({})

    def _read_json(self):
        try:
            return json.loads(self.path.read_text("utf-8"))
        except Exception:
            return {}

    def _write_json(self, obj):
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(obj, indent=2))
        tmp.replace(self.path)

    def has_cast(self, voter_hash: str) -> bool:
        return self._read_json().get(voter_hash, False)

    def mark_cast(self, voter_hash: str) -> None:
        data = self._read_json()
        data[voter_hash] = True
        self._write_json(data)
