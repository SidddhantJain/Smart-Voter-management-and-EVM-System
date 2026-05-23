from __future__ import annotations

from sqlalchemy.orm import Session

from backend.core.db import SessionLocal
from backend.core.models import User
from backend.core.security import hash_password


SUPERADMIN_EMAIL = "superadmin@voteguard.local"
SUPERADMIN_PASSWORD = "super12345"
SUPERADMIN_ROLE = "superadmin"


def ensure_superadmin() -> None:
    with SessionLocal() as db:
        existing = db.query(User).filter(User.email == SUPERADMIN_EMAIL).one_or_none()
        if existing is not None:
            return
        user = User(
            email=SUPERADMIN_EMAIL,
            hashed_password=hash_password(SUPERADMIN_PASSWORD),
            role=SUPERADMIN_ROLE,
        )
        db.add(user)
        db.commit()
