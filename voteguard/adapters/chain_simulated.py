from __future__ import annotations
from typing import Optional


class SimulatedAnchor:
    def anchor(self, record_hash: str) -> Optional[str]:
        # No real chain; return a deterministic pseudo anchor id
        return f"sim-{record_hash[:12]}"
