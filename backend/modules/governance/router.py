from __future__ import annotations

from fastapi import APIRouter


router = APIRouter(prefix="/governance", tags=["governance"])


@router.get("/audit")
def audit_overview() -> dict:
    return {"status": "ok", "message": "Audit workflow scaffolded.", "pending_actions": 0}


@router.get("/workflows")
def workflow_overview() -> dict:
    return {"status": "ok", "message": "Governance workflow scaffolded.", "queues": ["verification", "audit", "escalation"]}
