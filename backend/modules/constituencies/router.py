from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.db import get_db
from backend.core.models import AnalyticsEvent, Constituency


router = APIRouter(prefix="/constituencies", tags=["constituencies"])


class ConstituencyCreate(BaseModel):
    constituency_id: str
    name: str
    state: str | None = None
    district: str | None = None


class ConstituencyUpdate(BaseModel):
    name: str | None = None
    state: str | None = None
    district: str | None = None


@router.get("")
def list_constituencies(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(select(Constituency).order_by(Constituency.constituency_id)).all()
    return [
        {"constituency_id": row.constituency_id, "name": row.name, "state": row.state, "district": row.district}
        for row in rows
    ]


@router.post("")
def create_constituency(payload: ConstituencyCreate, db: Session = Depends(get_db)) -> dict:
    existing = db.get(Constituency, payload.constituency_id)
    if existing is not None:
        raise HTTPException(status_code=409, detail="Constituency already exists")

    record = payload.model_dump()
    db.add(Constituency(**record))
    db.add(AnalyticsEvent(event_type="constituency_created", payload={"constituency_id": payload.constituency_id}))
    db.commit()
    return {"status": "created", "constituency": record}


@router.put("/{constituency_id}")
def update_constituency(constituency_id: str, payload: ConstituencyUpdate, db: Session = Depends(get_db)) -> dict:
    constituency = db.get(Constituency, constituency_id)
    if constituency is None:
        raise HTTPException(status_code=404, detail="Constituency not found")

    for key, value in payload.model_dump().items():
        if value is not None:
            setattr(constituency, key, value)
    db.add(AnalyticsEvent(event_type="constituency_updated", payload={"constituency_id": constituency_id}))
    db.commit()
    return {
        "status": "updated",
        "constituency": {
            "constituency_id": constituency.constituency_id,
            "name": constituency.name,
            "state": constituency.state,
            "district": constituency.district,
        },
    }


@router.delete("/{constituency_id}")
def delete_constituency(constituency_id: str, db: Session = Depends(get_db)) -> dict:
    constituency = db.get(Constituency, constituency_id)
    if constituency is None:
        raise HTTPException(status_code=404, detail="Constituency not found")

    removed = {
        "constituency_id": constituency.constituency_id,
        "name": constituency.name,
        "state": constituency.state,
        "district": constituency.district,
    }
    db.delete(constituency)
    db.add(AnalyticsEvent(event_type="constituency_deleted", payload={"constituency_id": constituency_id}))
    db.commit()
    return {"status": "deleted", "constituency": removed}
