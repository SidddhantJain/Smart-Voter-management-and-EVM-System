from __future__ import annotations

from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.db import get_db
from backend.core.models import AnalyticsEvent, Constituency, Voter


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
def summary(db: Session = Depends(get_db)) -> dict:
    events = db.scalars(select(AnalyticsEvent)).all()
    event_types = Counter(event.event_type for event in events)
    return {
        "status": "ok",
        "voters": db.query(Voter).count(),
        "constituencies": db.query(Constituency).count(),
        "events": dict(event_types),
    }


@router.get("/events")
def events(db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(select(AnalyticsEvent).order_by(AnalyticsEvent.id.desc())).all()
    return {
        "status": "ok",
        "items": [
            {"id": row.id, "event_type": row.event_type, "payload": row.payload, "created_at": row.created_at.isoformat()}
            for row in rows
        ],
    }


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "message": "Analytics service scaffolded."}
