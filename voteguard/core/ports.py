from __future__ import annotations

from typing import Any, Dict, Optional, Protocol, Tuple

from .domain import AuditEvent, Receipt, Vote


class VoteStore(Protocol):
    def append_encrypted(self, vote: Vote) -> Tuple[int, str]:
        """Append encrypted vote; returns (seq, record_hash)."""
        ...


class AuditStore(Protocol):
    def append_event(self, event: AuditEvent) -> Tuple[int, str]: ...


class CastRegistry(Protocol):
    def has_cast(self, voter_hash: str) -> bool: ...

    def mark_cast(self, voter_hash: str) -> None: ...


class ChainAnchor(Protocol):
    def anchor(self, record_hash: str) -> Optional[str]:
        """Optionally anchor to a chain, return anchor id/tx or None."""
        ...


class BiometricPort(Protocol):
    def device_health(self) -> Dict[str, Any]: ...
