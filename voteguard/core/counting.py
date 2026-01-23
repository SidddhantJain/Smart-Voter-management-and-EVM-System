from __future__ import annotations
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Tuple
from cryptography.fernet import Fernet


def _read_ledger(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text("utf-8"))


def _verify_integrity(records: list) -> Tuple[bool, list]:
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
    return (len(errors) == 0), errors


def tally(ledger_path: Path, key_path: Path, verify: bool = True) -> Dict[str, Dict[str, int]]:
    """
    Tally votes from the encrypted hash-chained ledger.

    Returns a nested dict mapping election -> choice -> count.
    """
    if not ledger_path.exists():
        raise FileNotFoundError(f"Ledger not found: {ledger_path}")
    data = _read_ledger(ledger_path)
    records = data.get("records", [])

    if verify:
        ok, errors = _verify_integrity(records)
        if not ok:
            raise ValueError("Ledger integrity verification failed: " + "; ".join(errors))

    key = key_path.read_bytes()
    f = Fernet(key)
    result: Dict[str, Dict[str, int]] = {}
    for rec in records:
        ct = rec.get("ciphertext")
        if not ct:
            # skip non-vote records (e.g., audit ledgers use 'payload')
            continue
        pt = f.decrypt(ct.encode("utf-8"))
        obj = json.loads(pt.decode("utf-8"))
        vote = obj.get("vote", {})
        election = vote.get("election")
        choice = vote.get("choice")
        if not election or not choice:
            # malformed; skip without failing the tally
            continue
        by_election = result.setdefault(election, {})
        by_election[choice] = by_election.get(choice, 0) + 1

    return result
