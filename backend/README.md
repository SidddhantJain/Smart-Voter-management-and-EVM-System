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

## Database

Set `DATABASE_URL` to a PostgreSQL URL such as `postgresql+psycopg2://user:pass@localhost:5432/voteguard`.
If `DATABASE_URL` is not set, the app falls back to a local SQLite file for development.

## Migrations

```powershell
cd backend
alembic upgrade head
```

Alembic uses the same `DATABASE_URL`, so switching from SQLite to PostgreSQL is just an environment change.

## Database Helper

```powershell
python -m backend.manage_db upgrade
python -m backend.manage_db reset
python -m backend.manage_db current
```

Use `reset` to downgrade the schema to base and recreate it in one command.

## Included Modules

- `auth`
- `voters`
- `constituencies`
- `graph`
- `analytics`
- `governance`

These are scaffold endpoints only and are intended to be expanded into the full Nexus backend.
