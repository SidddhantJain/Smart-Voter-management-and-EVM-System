from __future__ import annotations

from typing import Any, Dict


class MockBiometric:
    def device_health(self) -> Dict[str, Any]:
        return {"camera": "ok", "fingerprint": "simulated", "retina": "simulated"}
