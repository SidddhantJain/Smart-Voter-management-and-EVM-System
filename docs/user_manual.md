# User Manual

This manual describes the common ways to use the Smart Voter Management and EVM System.

## 1. Main Application

Start the main application from the project root:

```powershell
python .\run_app.py
```

The main flow is:

1. Enter the voter details requested by the UI.
2. Continue through biometric or camera-assisted steps if enabled.
3. Review the ballot screen.
4. Cast the vote.
5. Confirm the on-screen success message.

## 2. Counting and Tally Tools

Use the counting UI when you need to inspect or export vote results:

```powershell
python .\run_count_app.py
```

Use the tally script for command-line counting tasks:

```powershell
python .\run_tally.py
```

For simulation and validation:

```powershell
python .\scripts\simulate_votes.py
python .\scripts\tally_votes.py
python .\scripts\verify_ledger.py .\data\ballot_ledger.json
```

## 3. Camera Demo

If camera support and model files are installed, you can run the demo capture view:

```powershell
python .\scripts\demo_camera_detection.py
```

If overlays are distracting or not required, set `VOTEGUARD_OVERLAYS=0` before launching the demo.

## 4. IPFS and Audit Features

If you have a local IPFS node available, the counting and admin tools can anchor exported files and show CIDs.

Typical local endpoints are:

- API: `http://127.0.0.1:5001`
- Gateway: `http://127.0.0.1:8080`

Useful actions in the app include:

- Exporting results to JSON.
- Viewing the last recorded IPFS CID.
- Verifying a CID against the current local results or audit ledger.

## 5. What the User Should Expect

- The app is designed to be simulation-friendly, so not every feature requires external hardware.
- If camera or ML support is missing, the system should still allow the main voting flow to continue.
- The ballot and audit ledgers are stored locally and are intended to be treated as protected data.

## 6. Practical Tips

- Use the same working directory when launching the scripts so relative paths resolve correctly.
- Keep the Fernet key consistent with the data files you are reading or writing.
- If a feature appears unavailable, check whether the optional dependency set for that feature was installed.