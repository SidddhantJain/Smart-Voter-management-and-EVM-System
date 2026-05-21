from __future__ import annotations

import json
import socket
from typing import Any, Dict


class VerificationClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 8785, timeout_seconds: float = 3.0):
        self.host = host
        self.port = port
        self.timeout_seconds = timeout_seconds

    def _send(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        with socket.create_connection((self.host, self.port), timeout=self.timeout_seconds) as connection:
            connection.sendall((json.dumps(payload) + "\n").encode("utf-8"))
            response = connection.makefile("r", encoding="utf-8").readline()
        if not response:
            raise RuntimeError("empty response from verification server")
        return json.loads(response)

    def submit(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._send({"action": "submit", "payload": payload})

    def status(self, request_id: str) -> Dict[str, Any]:
        return self._send({"action": "status", "request_id": request_id})

    def wait_for_result(self, request_id: str, timeout_seconds: float = 20.0, poll_interval_seconds: float = 0.5) -> Dict[str, Any]:
        import time

        deadline = time.time() + timeout_seconds
        result: Dict[str, Any] = {"status": "pending"}
        while time.time() < deadline:
            result = self.status(request_id)
            if result.get("status") in {"approved", "rejected"}:
                return result
            time.sleep(poll_interval_seconds)
        return result
