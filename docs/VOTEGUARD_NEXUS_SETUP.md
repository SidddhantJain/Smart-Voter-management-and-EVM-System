# VoteGuard Nexus Setup and Adoption Blueprint

This repository is currently a Python-first prototype. The VoteGuard Nexus prompt below is treated here as a target architecture and an implementation roadmap, not as something already fully present in the codebase.

## What Is Already In This Repo

- Python prototype UI and workflows under `voteguard/` and `Phase 1A - Foundation/Month 3 - Prototype Development/EVM IoT Application/src`.
- Manual server approval flow under `server/`.
- Camera and biometric simulation utilities under `scripts/` and the PyQt UI.
- Existing optional requirements files for camera, ML, and blockchain experiments.

## What Needs To Be Installed

### Core Software

- Python 3.11 or later
- Git
- Visual Studio Code
- Windows PowerShell

### Backend / API Stack For Nexus

- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic
- Celery
- Redis

### Database / Infrastructure

- PostgreSQL
- PostGIS
- Neo4j

### Frontend Stack

- Node.js 20 or later
- npm or pnpm
- Next.js
- TypeScript
- TailwindCSS
- ShadCN UI
- Framer Motion
- React Query
- Zustand

### Visualization / GIS

- Cytoscape.js
- D3.js
- Three.js
- Deck.gl
- Leaflet
- Mapbox GL

### AI / ML

- NumPy
- Pandas
- Scikit-learn
- XGBoost
- PyTorch (optional)

### DevOps / Deployment

- GitHub Actions
- Nginx
- Docker and Docker Compose are optional and deferred on this laptop.

## Python Packages Already Referenced By This Repo

- `cryptography`
- `PyQt5`
- `pyqtgraph`
- `pytest`
- `opencv-contrib-python` for camera extras
- `onnxruntime` for ML extras
- `requests`

## Existing Requirement Files

- [requirements-base.txt](../requirements-base.txt)
- [requirements-camera.txt](../requirements-camera.txt)
- [requirements-ml.txt](../requirements-ml.txt)
- [requirements-blockchain.txt](../requirements-blockchain.txt)

## Recommended Install Order

1. Install Python 3.11+ and Git.
2. Create and activate a virtual environment.
3. Install the base requirements.
4. Install camera or ML extras only if you need the webcam or analytics demos.
5. Install Node.js only when the Next.js frontend is added.
6. Install PostgreSQL, Redis, and Neo4j when the backend services are actually introduced.
7. Skip Docker and Docker Compose on this laptop; use them later only on hardware that supports them reliably.

## How This Prompt Maps To The Current Repo

The best fit for this repository is to evolve it in stages:

1. Preserve the current PyQt prototype and verification server.
2. Add a modular backend package for FastAPI under a new `backend/` tree.
3. Add a separate Next.js frontend when the UI split is ready.
4. Introduce optional graph, GIS, and AI modules behind clean interfaces.
5. Keep the current prototype runnable while the Nexus modules are added.

## Development And Implementation Integration With The System

The implementation should not replace the current prototype in one step. It should integrate with the system incrementally so the app remains usable at every stage.

### Integration Order

1. Keep the existing PyQt voter flow, camera flow, and server approval flow as the stable baseline.
2. Add a FastAPI backend alongside the current Python prototype instead of moving everything at once.
3. Route new voter, constituency, graph, and analytics features through backend service interfaces.
4. Expose the new backend through the existing admin and operator workflows first.
5. Move the browser-based dashboard and analytical views to Next.js after the backend APIs are stable.
6. Add AI, GIS, and graph services as plug-in style modules so they can be developed independently.

### Current-System Integration Points

- `run_app.py` remains the primary launcher for the current prototype and can be extended to launch new modules.
- `server/` remains the approval and verification gateway for operator workflows.
- `voteguard/config/` remains the shared settings layer for host, port, and election configuration.
- `scripts/` remains the operational tooling area for training, camera checks, and data preparation.
- `docs/` remains the place where architecture, setup, and migration steps are recorded.

### Practical Development Phases

1. Stabilize the current prototype and manual approval workflow.
2. Scaffold `backend/modules/auth`, `backend/modules/voters`, and `backend/modules/governance`.
3. Add database models and API schemas for voter and constituency data.
4. Add graph and GIS endpoints behind read-only APIs.
5. Add AI fraud scoring after the data model is stable.
6. Build the Next.js dashboards once the backend APIs stop changing frequently.

### Compatibility Rule

The current system must continue to run even while Nexus modules are being added. New code should be optional until it is fully wired into the existing launchers and tested.

## Notes

- This document is the installation and architecture checkpoint for the new advanced prototype branch.
- If you want the repo to become a true Nexus implementation, the next step is scaffolding `backend/` and `frontend/` in separate phases.