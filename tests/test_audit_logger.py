import os
import json
import tempfile
from pathlib import Path

from voteguard.adapters.audit_helper import SafeAuditLogger
from voteguard.config.env import data_dir


def _read_audit(path: Path):
    return json.loads(path.read_text("utf-8"))


def test_audit_session_correlation():
    # Use temp data dir to isolate ledger
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["VOTEGUARD_DATA"] = tmp
        logger = SafeAuditLogger()
        logger.log("TEST_EVENT", {"session_id": "abc123", "flag": True})
        # Verify audit file exists and contains the session_id in payload
        audit_path = Path(tmp) / "audit_ledger.json"
        assert audit_path.exists(), "audit ledger should be created"
        data = _read_audit(audit_path)
        assert "records" in data
        assert len(data["records"]) == 1
        payload = json.loads(data["records"][0]["payload"])  # stringified JSON
        assert payload["kind"] == "TEST_EVENT"
        assert payload["details"]["session_id"] == "abc123"
        assert payload["details"]["flag"] is True


def test_audit_best_effort_swallow_errors():
    class BadAudit:
        def append_event(self, evt):
            raise RuntimeError("simulated failure")

    with tempfile.TemporaryDirectory() as tmp:
        os.environ["VOTEGUARD_DATA"] = tmp
        logger = SafeAuditLogger()
        # Ledger exists but has zero records initially
        audit_path = Path(tmp) / "audit_ledger.json"
        data = _read_audit(audit_path)
        assert len(data["records"]) == 0
        # Replace internal audit adapter with one that raises on append
        logger._audit = BadAudit()
        # Should not raise despite failure
        logger.log("WONT_WRITE", {"x": 1})
        # Records remain unchanged
        data2 = _read_audit(audit_path)
        assert len(data2["records"]) == 0
