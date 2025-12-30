# Security Model and Assurances

Assumptions:
- Prototype runs in simulation mode; no production blockchain; hardware and FFI are optional.
- Keys are file-based for development only; production requires external secret storage.

Threats:
- Tampering with stored ballots or audit logs.
- Double-voting attempts via repeated identifiers.
- Faulty or malicious device outputs.

Protections:
- Hash-chained, append-only ledgers for ballots and audit events.
- Fernet encryption for ballot payloads (no PII stored).
- Salted hash cast registry stored separately from ballot ledger.
- Deterministic state machine; accessibility failures are correctness failures.

Detection:
- Verifier detects missing sequence numbers and hash mismatches without blockchain.
- Audit chain captures device and adapter failures.

Non-goals:
- End-to-end verifiability at voter scale; hardware root of trust; on-chain consensus.
