from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    role: str = "voter"


@router.post("/login")
def login(payload: LoginRequest) -> dict:
    return {"status": "ok", "message": "Login endpoint scaffolded.", "email": payload.email}


@router.post("/register")
def register(payload: RegisterRequest) -> dict:
    return {"status": "ok", "message": "Registration endpoint scaffolded.", "email": payload.email, "role": payload.role}


@router.post("/refresh")
def refresh() -> dict:
    return {"status": "ok", "message": "Token refresh endpoint scaffolded."}
