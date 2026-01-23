# Run & Verify (Windows PowerShell)

## Setup
- Optional overlays are controlled by env `VOTEGUARD_OVERLAYS`.
- Place ML models under `Phase 1A - Foundation/models` (see README).

```powershell
# (Optional) enable overlays for camera UI
$env:VOTEGUARD_OVERLAYS = "1"
```

## Simulation
```powershell
# Simulate N votes (default settings)
python .\scripts\simulate_votes.py

# Verify ballot ledger integrity
python .\scripts\verify_ledger.py .\data\ballot_ledger.json

# Verify audit ledger integrity
python .\scripts\verify_ledger.py .\data\audit_ledger.json
```

## UI Applications
```powershell
# Main UI app
python .\run_app.py

# Counting UI
python .\run_count_app.py

# Tally runner (CLI)
python .\run_tally.py
```

## Camera Demo
```powershell
# Run camera demo with overlays if models are present
python .\scripts\demo_camera_detection.py
```

## Casting & Tally Helpers
```powershell
# Cast a single vote via script (simulation)
python .\scripts\cast_vote.py

# Tally votes from ballot ledger
python .\scripts\tally_votes.py
```

## Tests
```powershell
# Run project tests
python -m pytest .\tests
```

## Formatting & CI Checks
```powershell
# Sort imports and format (local)
isort . --profile black
black .

# Check-only (CI-like)
isort . --profile black --check-only "Phase 1A - Foundation/Month 3 - Prototype Development/EVM IoT Application/src" voteguard scripts tests
black --check "Phase 1A - Foundation/Month 3 - Prototype Development/EVM IoT Application/src" voteguard scripts tests
```

Notes:
- The counting UI reads from `data/ballot_ledger.json` and decrypts using `key.key`.
- No Aadhaar/Voter ID is written to the ballot or audit ledgers; only salted hashes are in the cast registry.
- Missing ML models, hardware, or blockchain binaries do not prevent simulation.
