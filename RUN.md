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

## IPFS & Audit Tools (Optional)

If you run a local IPFS node (for example, IPFS Desktop), you can anchor exported results and audit snapshots:

1. Start IPFS Desktop and ensure the API is reachable:
	```powershell
	ping 127.0.0.1
	```
	The IPFS HTTP API is expected at `http://127.0.0.1:5001` and the gateway at `http://127.0.0.1:8080`.

2. Launch the counting UI:
	```powershell
	python .\run_count_app.py
	```

3. From the counting window:
	- Use **Export JSON** / **Export Filtered JSON** to save results. When IPFS is available, the app will also add the exported JSON to IPFS and show the resulting CID in the success dialog.
	- Use **View Last IPFS CID** to open the most recently exported CID in your default browser via the local IPFS gateway.

4. From the admin panel (launched from the main UI):
	- **Show Recent IPFS CIDs** lists the most recent IPFS-related audit events and their CIDs.
	- **Verify IPFS CID…** fetches the content for a given CID from IPFS and checks whether it matches the current `data/results.json` or `data/audit_ledger.json` files.

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
 
    