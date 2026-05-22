from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


router = APIRouter(prefix="/voters", tags=["voters"])
_voters: List[dict] = []


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
def list_voters() -> list[dict]:
    return _voters


@router.post("")
def create_voter(payload: VoterCreate) -> dict:
    record = payload.model_dump()
    _voters.append(record)
    return {"status": "created", "voter": record}


@router.put("/{voter_id}")
def update_voter(voter_id: str, payload: VoterUpdate) -> dict:
    for voter in _voters:
        if voter["voter_id"] == voter_id:
            voter.update({key: value for key, value in payload.model_dump().items() if value is not None})
            return {"status": "updated", "voter": voter}
    raise HTTPException(status_code=404, detail="Voter not found")


@router.delete("/{voter_id}")
def delete_voter(voter_id: str) -> dict:
    for index, voter in enumerate(_voters):
        if voter["voter_id"] == voter_id:
            removed = _voters.pop(index)
            return {"status": "deleted", "voter": removed}
    raise HTTPException(status_code=404, detail="Voter not found")
