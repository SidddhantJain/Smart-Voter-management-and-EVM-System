from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Tuple

from ..core.domain import AuditEvent


class HashChainedAudit:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write_json(
                {"header": {"version": 1, "created_at": time.time()}, "records": []}
            )

    def _read_json(self):
        return json.loads(self.path.read_text("utf-8"))

    def _write_json(self, obj):
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(obj, indent=2))
        tmp.replace(self.path)

    def append_event(self, event: AuditEvent) -> Tuple[int, str]:
        data = self._read_json()
        records = data.get("records", [])
        seq = len(records) + 1
        prev_hash = records[-1]["record_hash"] if records else "0" * 64
        payload = json.dumps(
            {"kind": event.kind, "details": event.details, "at": event.at},
            separators=(",", ":"),
        )
        record_hash = hashlib.sha256(
            (prev_hash + ":" + payload + ":" + str(seq)).encode("utf-8")
        ).hexdigest()
        records.append(
            {
                "seq": seq,
                "prev_hash": prev_hash,
                "payload": payload,
                "record_hash": record_hash,
            }
        )
        data["records"] = records
        self._write_json(data)
        return seq, record_hash
