# VoteGuard Nexus Backend Scaffold

This folder is the first modular-monolith backend slice for VoteGuard Nexus.

## Install

```powershell
python -m pip install -r backend/requirements.txt
```

## Run

```powershell
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

## Included Modules

- `auth`
- `voters`
- `governance`

These are scaffold endpoints only and are intended to be expanded into the full Nexus backend.
