# Installation and Setup Guide

This guide explains how to install and prepare the Smart Voter Management and EVM System on Windows.

## 1. Prerequisites

Install the following before running the project:

- Python 3.11 or newer.
- PowerShell on Windows.
- Optional: a local IPFS Desktop node if you want to use IPFS export and verification features.
- Optional: camera hardware and model files if you want to run the camera and ML demos.

## 2. Get the Project Ready

1. Open the repository folder in VS Code or File Explorer.
2. Confirm that the top-level files such as `run_app.py`, `RUN.md`, and `requirements-base.txt` are present.
3. If you are starting from a clean clone, create a virtual environment in the project root.

```powershell
python -m venv .venv
```

4. Activate the environment.

```powershell
.\.venv\Scripts\Activate.ps1
```

## 3. Install Dependencies

Install the base dependencies first.

```powershell
pip install -r .\requirements-base.txt
```

Install optional extras only if you need them:

```powershell
pip install -r .\requirements-camera.txt
pip install -r .\requirements-ml.txt
pip install -r .\requirements-blockchain.txt
```

If you want the package installed in editable mode for development, you can also run:

```powershell
pip install -e .
```

## 4. Configure Environment Files

1. Copy `.env.example` to `.env` if you want to use environment-based configuration.
2. Set `FERNET_KEY_PATH` to the key file you want to use for encrypted vote storage.
3. Set `VOTEGUARD_OVERLAYS=0` if you want to disable camera and UI overlays.
4. Set `VOTEGUARD_DATA` if you want the app to read and write its data directory somewhere other than `./data`.

## 5. Prepare Model Assets

If you plan to use the camera and ML demo features, place model files under `Phase 1A - Foundation/models`.

Typical files include:

- Emotion model files for overlay inference.
- Age and gender model files if you want demographic overlay support.

If the model directory is missing, the app falls back to a local `./models` path when available.

## 6. Run the Application

Launch the main UI from the project root.

```powershell
python .\run_app.py
```

Optional related entry points:

```powershell
python .\run_count_app.py
python .\run_tally.py
python .\scripts\demo_camera_detection.py
```

## 7. Verify the Installation

Use the included verification commands to confirm that the environment is working.

```powershell
python .\scripts\simulate_votes.py
python .\scripts\verify_ledger.py .\data\ballot_ledger.json
python -m pytest .\tests
```

## 8. Common Setup Notes

- Keep `key.key` and other secret material outside source control.
- The base installation is designed to work even when camera, ML, or blockchain extras are not installed.
- If the UI fails to launch, verify that PyQt5 installed correctly in the active virtual environment.