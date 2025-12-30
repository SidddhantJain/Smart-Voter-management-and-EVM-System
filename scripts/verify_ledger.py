import json
import sys
from pathlib import Path
import hashlib


def verify(path: Path) -> int:
    data = json.loads(path.read_text("utf-8"))
    records = data.get("records", [])
    prev_hash = "0" * 64
    expected_seq = 1
    errors = []
    for rec in records:
        seq = rec.get("seq")
        if seq != expected_seq:
            errors.append(f"Missing or out-of-order seq: expected {expected_seq}, found {seq}")
        payload = rec.get("ciphertext") or rec.get("payload")
        calc = hashlib.sha256((prev_hash + ":" + payload + ":" + str(seq)).encode("utf-8")).hexdigest()
        if calc != rec.get("record_hash"):
            errors.append(f"Hash mismatch at seq {seq}")
        prev_hash = rec.get("record_hash")
        expected_seq += 1
    if errors:
        print("INTEGRITY: FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("INTEGRITY: OK (records=", len(records), ")")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/verify_ledger.py <path-to-ledger.json>")
        sys.exit(2)
    sys.exit(verify(Path(sys.argv[1])))
