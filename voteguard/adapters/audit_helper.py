from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
from ..config.env import data_dir
from ..adapters.audit_log_hashchain import HashChainedAudit
from ..core.domain import AuditEvent


class SafeAuditLogger:
    def __init__(self):
        try:
            self._audit = HashChainedAudit(data_dir() / "audit_ledger.json")
        except Exception:
            self._audit = None

    def log(self, kind: str, details: Dict[str, Any]) -> None:
        try:
            if self._audit is None:
                self._audit = HashChainedAudit(data_dir() / "audit_ledger.json")
            self._audit.append_event(AuditEvent.now(kind, details))
        except Exception:
            # Never throw; audit is best-effort
            pass
