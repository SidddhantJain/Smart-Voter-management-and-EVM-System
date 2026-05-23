from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.db import get_db
from backend.core.models import GraphEdge as GraphEdgeRecord
from backend.core.models import GraphNode as GraphNodeRecord


router = APIRouter(prefix="/graph", tags=["graph"])


class GraphNodePayload(BaseModel):
    id: str
    label: str
    kind: str


class GraphEdgePayload(BaseModel):
    source: str
    target: str
    relation: str


@router.get("/network")
def get_network(db: Session = Depends(get_db)) -> dict:
    nodes = db.scalars(select(GraphNodeRecord)).all()
    edges = db.scalars(select(GraphEdgeRecord)).all()
    return {
        "nodes": [{"id": node.id, "label": node.label, "kind": node.kind} for node in nodes],
        "edges": [{"source": edge.source, "target": edge.target, "relation": edge.relation} for edge in edges],
    }


@router.post("/nodes")
def add_node(payload: GraphNodePayload, db: Session = Depends(get_db)) -> dict:
    record = payload.model_dump()
    db.merge(GraphNodeRecord(**record))
    db.commit()
    return {"status": "created", "node": record}


@router.post("/edges")
def add_edge(payload: GraphEdgePayload, db: Session = Depends(get_db)) -> dict:
    record = payload.model_dump()
    db.add(GraphEdgeRecord(**record))
    db.commit()
    return {"status": "created", "edge": record}


@router.get("/summary")
def graph_summary(db: Session = Depends(get_db)) -> dict:
    return {"status": "ok", "nodes": db.query(GraphNodeRecord).count(), "edges": db.query(GraphEdgeRecord).count()}
