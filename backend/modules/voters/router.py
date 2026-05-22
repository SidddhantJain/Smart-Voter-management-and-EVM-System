from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.db import get_db
from backend.core.models import AnalyticsEvent, Voter


router = APIRouter(prefix="/voters", tags=["voters"])


class VoterCreate(BaseModel):
    voter_id: str
    first_name: str
    last_name: str
    constituency: str | None = None


class VoterUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    constituency: str | None = None


@router.get("")
def list_voters(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(select(Voter).order_by(Voter.voter_id)).all()
    return [
        {"voter_id": row.voter_id, "first_name": row.first_name, "last_name": row.last_name, "constituency": row.constituency}
        for row in rows
    ]


@router.post("")
def create_voter(payload: VoterCreate, db: Session = Depends(get_db)) -> dict:
    existing = db.get(Voter, payload.voter_id)
    if existing is not None:
        raise HTTPException(status_code=409, detail="Voter already exists")

    record = payload.model_dump()
    db.add(Voter(**record))
    db.add(AnalyticsEvent(event_type="voter_created", payload={"voter_id": payload.voter_id}))
    db.commit()
    return {"status": "created", "voter": record}


@router.put("/{voter_id}")
def update_voter(voter_id: str, payload: VoterUpdate, db: Session = Depends(get_db)) -> dict:
    voter = db.get(Voter, voter_id)
    if voter is None:
        raise HTTPException(status_code=404, detail="Voter not found")

    for key, value in payload.model_dump().items():
        if value is not None:
            setattr(voter, key, value)
    db.add(AnalyticsEvent(event_type="voter_updated", payload={"voter_id": voter_id}))
    db.commit()
    return {
        "status": "updated",
        "voter": {"voter_id": voter.voter_id, "first_name": voter.first_name, "last_name": voter.last_name, "constituency": voter.constituency},
    }


@router.delete("/{voter_id}")
def delete_voter(voter_id: str, db: Session = Depends(get_db)) -> dict:
    voter = db.get(Voter, voter_id)
    if voter is None:
        raise HTTPException(status_code=404, detail="Voter not found")

    removed = {"voter_id": voter.voter_id, "first_name": voter.first_name, "last_name": voter.last_name, "constituency": voter.constituency}
    db.delete(voter)
    db.add(AnalyticsEvent(event_type="voter_deleted", payload={"voter_id": voter_id}))
    db.commit()
    return {"status": "deleted", "voter": removed}
