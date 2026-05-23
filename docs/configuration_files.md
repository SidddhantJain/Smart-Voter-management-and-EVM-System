# Configuration Files

This document summarizes the configuration files and environment variables used by the project.

## 1. Primary Configuration Files

- `.env.example` provides the baseline environment template.
- `key.key` is the Fernet key file used for encrypted vote storage when file-based key loading is enabled.
- `data/` contains the local JSON ledgers used by the application.
- `Phase 1A - Foundation/models/README.md` explains where to place optional model assets.

## 2. Environment Variables

The codebase currently reads these values:

- `VOTEGUARD_DATA` for the data directory.
- `FERNET_KEY_PATH` for the key file path.
- `FERNET_KEY` for a base64-encoded Fernet key value.
- `VOTEGUARD_OVERLAYS` for global camera and UI overlay control.
- `ENABLE_CAMERA` for camera feature toggles in the packaged `voteguard` configuration helpers.
- `ENABLE_ML` for ML feature toggles in the packaged `voteguard` configuration helpers.
- `ML_MODEL_DIR` for alternate model locations when the default model folder is absent.

## 3. Sample `.env`

You can start from the repository template and adjust the values for your environment.

```env
# Encrypted vote storage
VOTE_STORAGE_PATH=./votes.json
FERNET_KEY_PATH=./key.key

# Audit logging
AUDIT_LOG_PATH=./audit_log.enc

# Optional camera and ML toggles
ENABLE_CAMERA=0
ENABLE_ML=0
VOTEGUARD_OVERLAYS=1

# Optional model override
ML_MODEL_DIR=./models

# Blockchain client placeholders
WEB3_PROVIDER_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=0xYourContractAddress

# Optional direct key override
# FERNET_KEY=base64-encoded-fernet-key
```

## 4. Recommended Local Setup

1. Copy `.env.example` to `.env`.
2. Set `FERNET_KEY_PATH` to a secure location outside the repository if possible.
3. Decide whether overlays should be enabled for your environment.
4. Add model files only if you are using the camera and ML features.

## 5. Secrets and Safety

- Do not commit real secret material to the repository.
- Keep the Fernet key aligned with the vote and audit ledgers that were written with it.
- If you rotate the key, expect existing encrypted files to become unreadable until they are reinitialized.