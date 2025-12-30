from __future__ import annotations
from typing import Dict, Any


class MockBiometric:
    def device_health(self) -> Dict[str, Any]:
        return {"camera": "ok", "fingerprint": "simulated", "retina": "simulated"}
