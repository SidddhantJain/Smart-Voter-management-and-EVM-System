# VoteGuard Pro Architecture

This document defines the Clean Architecture refactor: core (domain, ports, use cases, state machine) is framework-agnostic; adapters implement ports; configuration centralizes environment concerns. UI, ML, and blockchain are optional adapters.

Directory:

```
voteguard/
  core/
    domain.py
    ports.py
    usecases.py
    state_machine.py
  adapters/
    storage_fernet_hashchain.py
    audit_log_hashchain.py
    devices_mock.py
    chain_simulated.py
  config/
    env.py
    secrets.py
  app.py
```

Dependency rules:
- core imports nothing from adapters or external frameworks.
- adapters implement ports and may depend on libraries (Fernet, OpenCV, web3, etc.).
- UI depends on core and adapters only through ports.

Data flow:
- Use case `CastVote` → `VoteStore.append_encrypted` → hash-chained ledger.
- `AuditStore.append_event` logs operational events in a parallel chain.
- `CastRegistry` prevents double-voting using salted hashes.
- `ChainAnchor` optionally anchors record hashes.
