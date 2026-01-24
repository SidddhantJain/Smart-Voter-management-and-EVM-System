from __future__ import annotations

import hashlib
import os
import secrets
import time
from typing import Optional

from .domain import AuditEvent, Receipt, Vote
from .ports import AuditStore, CastRegistry, ChainAnchor, VoteStore


def salted_hash(identifier: str, salt: str) -> str:
    return hashlib.sha256((salt + ":" + identifier).encode("utf-8")).hexdigest()


class CastVote:
    def __init__(
        self,
        vote_store: VoteStore,
        audit_store: AuditStore,
        registry: CastRegistry,
        chain: Optional[ChainAnchor] = None,
        salt: Optional[str] = None,
    ):
        self.vote_store = vote_store
        self.audit_store = audit_store
        self.registry = registry
        self.chain = chain
        self.salt = salt or os.getenv("VOTER_HASH_SALT", "demo-salt")

    def execute(
        self, election: str, choice: str, aadhaar: str, voter_id: str
    ) -> Receipt:
        voter_hash = salted_hash(aadhaar + "|" + voter_id, self.salt)
        if self.registry.has_cast(voter_hash):
            self.audit_store.append_event(
                AuditEvent.now(
                    "double_vote_blocked", {"voter_hash_prefix": voter_hash[:8]}
                )
            )
            raise ValueError("Voter has already cast a ballot")

        vote = Vote(election=election, choice=choice)  # no PII
        seq, record_hash = self.vote_store.append_encrypted(vote)
        self.registry.mark_cast(voter_hash)
        self.audit_store.append_event(
            AuditEvent.now("vote_stored", {"seq": seq, "record_hash": record_hash})
        )
        if self.chain is not None:
            anchor_id = self.chain.anchor(record_hash)
            self.audit_store.append_event(
                AuditEvent.now(
                    "anchor_attempt",
                    {"seq": seq, "record_hash": record_hash, "anchor_id": anchor_id},
                )
            )
        nonce = secrets.token_hex(8)
        receipt_id = hashlib.sha256(
            (record_hash + ":" + str(time.time()) + ":" + nonce).encode("utf-8")
        ).hexdigest()
        return Receipt(receipt_id=receipt_id, seq=seq, created_at=time.time())
