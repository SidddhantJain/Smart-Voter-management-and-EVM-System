# Developer Guide

This guide is for contributors who want to maintain or extend the project.

## 1. Project Structure

The main implementation is split across these areas:

- `voteguard/` for the packaged core application and adapters.
- `scripts/` for simulation, tally, verification, and visualization utilities.
- `tests/` for automated checks.
- `Phase 1A - Foundation/Month 3 - Prototype Development/EVM IoT Application/` for the larger prototype source tree and supporting assets.

## 2. Key Runtime Entry Points

- `run_app.py` launches the primary UI.
- `run_count_app.py` launches the counting UI.
- `run_tally.py` runs tally-related logic.
- `scripts/demo_camera_detection.py` exercises camera overlays and recognition paths.

## 3. Recommended Development Setup

1. Create and activate a virtual environment.
2. Install the base requirements from `requirements-base.txt`.
3. Install any optional requirements that your change touches.
4. Run the smallest relevant script or test first.

Example:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r .\requirements-base.txt
pip install -e .
```

## 4. Testing

Run the test suite with:

```powershell
python -m pytest .\tests
```

For targeted development, prefer the narrowest relevant test file before running the full suite.

## 5. Formatting and Validation

The repository already references import sorting and formatting checks in `RUN.md`. A typical local workflow is:

```powershell
isort . --profile black
black .
```

Use check-only variants before submitting changes when you want a non-destructive validation pass.

## 6. Configuration Contracts

Pay attention to these environment variables and file locations when making changes:

- `VOTEGUARD_DATA` controls the data directory.
- `FERNET_KEY_PATH` controls the key file used for encrypted storage.
- `FERNET_KEY` can override key-file loading for the logger path.
- `VOTEGUARD_OVERLAYS` enables or disables visual overlays.
- `Phase 1A - Foundation/models` is the default model location when present.

## 7. Extension Guidelines

- Keep the main voting flow working without optional camera, ML, or blockchain dependencies.
- Treat biometric and demographic modules as auxiliary features, not as access-control gates.
- Preserve local encrypted storage behavior when touching ballot or audit code.
- Add or update tests when you change persistence, validation, or state transitions.

## 8. Known Sensitivities

- Avoid hardcoding secrets into source files.
- Be careful when changing default paths, because many scripts rely on relative locations.
- If you modify ledger formats, update both the runtime code and the verification utilities.