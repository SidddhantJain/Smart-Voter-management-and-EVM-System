# Run & Verify

Simulation Mode (default):

```powershell
# Create data directory and run simulation of N votes
python .\scripts\simulate_votes.py

# Verify ballot ledger integrity
python .\scripts\verify_ledger.py .\data\ballot_ledger.json

# Verify audit ledger integrity (if used elsewhere)
python .\scripts\verify_ledger.py .\data\audit_ledger.json
```

UI Demo (unchanged):
```powershell
python .\run_app.py
```

Notes:
- No Aadhaar/Voter ID is written to the ballot ledger or audit ledger; only salted hashes are kept in the cast registry.
- Missing ML models, hardware, or blockchain binaries do not prevent simulation.
