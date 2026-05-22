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
    from fastapi import HTTPException, Depends
    from sqlalchemy.orm import Session
    from backend.core.db import get_db
    from backend.core.models import User
    from backend.core.security import verify_password, create_access_token

    db: Session = next(get_db())
    user = db.query(User).filter(User.email == payload.email).one_or_none()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(subject=user.id)
    return {"status": "ok", "access_token": token, "token_type": "bearer", "email": user.email, "role": user.role}


@router.post("/register")
def register(payload: RegisterRequest) -> dict:
    from fastapi import HTTPException
    from sqlalchemy.orm import Session
    from backend.core.db import get_db
    from backend.core.models import User
    from backend.core.security import hash_password, create_access_token

    db: Session = next(get_db())
    existing = db.query(User).filter(User.email == payload.email).one_or_none()
    if existing is not None:
        raise HTTPException(status_code=409, detail="User already exists")
    if payload.role == "superadmin":
        raise HTTPException(status_code=403, detail="Superadmin accounts are provisioned automatically")
    user = User(email=payload.email, hashed_password=hash_password(payload.password), role=payload.role)
    db.add(user)
    db.commit()
    token = create_access_token(subject=user.id)
    return {"status": "created", "access_token": token, "token_type": "bearer", "email": user.email, "role": user.role}


@router.post("/refresh")
def refresh() -> dict:
    return {"status": "ok", "message": "Token refresh endpoint scaffolded."}
