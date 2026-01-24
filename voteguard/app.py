from __future__ import annotations

from pathlib import Path

from .adapters.audit_log_hashchain import HashChainedAudit
from .adapters.chain_simulated import SimulatedAnchor
from .adapters.devices_mock import MockBiometric
from .adapters.storage_fernet_hashchain import HashChainedLedger, JsonCastRegistry
from .config.env import data_dir, key_path, overlays_enabled
from .core.usecases import CastVote


def bootstrap():
    d = data_dir()
    ledger = HashChainedLedger(d / "ballot_ledger.json", key_path())
    audit = HashChainedAudit(d / "audit_ledger.json")
    registry = JsonCastRegistry(d / "cast_registry.json")
    chain = SimulatedAnchor()
    biometrics = MockBiometric()
    return CastVote(ledger, audit, registry, chain)


# Global overlays toggle available to UI/camera components
OVERLAYS_ENABLED = overlays_enabled()
