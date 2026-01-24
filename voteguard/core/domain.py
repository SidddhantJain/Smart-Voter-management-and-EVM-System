from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional

VoteChoice = str  # candidate identifier or name (no PII)
ElectionType = Literal["GENERAL", "STATE", "LOCAL"]


@dataclass(frozen=True)
class Vote:
    election: ElectionType
    choice: VoteChoice
    created_at: float = dataclass(init=False, repr=False)  # wallclock for metadata only

    def to_public_json(self) -> Dict[str, Any]:
        # Only non-PII, non-linkable fields
        return {"election": self.election, "choice": self.choice}


@dataclass(frozen=True)
class Receipt:
    receipt_id: str  # SHA256(record_hash || timestamp || nonce)
    seq: int
    created_at: float


@dataclass(frozen=True)
class AuditEvent:
    kind: str
    details: Dict[str, Any]
    at: float

    @staticmethod
    def now(kind: str, details: Dict[str, Any]) -> "AuditEvent":
        return AuditEvent(kind=kind, details=details, at=time.time())
