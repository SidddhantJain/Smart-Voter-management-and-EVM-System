from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..adapters.audit_log_hashchain import HashChainedAudit
from ..config.env import data_dir
from ..core.domain import AuditEvent

try:
    # Optional IPFS helper; may not be available in all runtimes.
    # This allows the core voteguard library to run even when the
    # EVM IoT Application sources (with backend.ipfs_client) are not present.
    from backend import ipfs_client  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    ipfs_client = None  # type: ignore


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

    def snapshot_to_ipfs(self) -> None:
        """Best-effort snapshot of the current audit ledger to IPFS.

        This is intended to be called at key moments (e.g., after
        final certification / results export) so that the entire
        audit_ledger.json file is pinned to IPFS and the resulting CID
        is recorded back into the audit log.
        """

        if ipfs_client is None or not getattr(ipfs_client, "add_file", None):
            return

        try:
            path = data_dir() / "audit_ledger.json"
            cid = ipfs_client.add_file(path)
        except Exception:
            return

        if not cid:
            return

        try:
            if self._audit is None:
                self._audit = HashChainedAudit(path)
            self._audit.append_event(
                AuditEvent.now(
                    "AUDIT_LEDGER_SNAPshOT_IPFS",
                    {"path": str(path), "ipfs_cid": cid},
                )
            )
        except Exception:
            # Still best-effort
            pass
