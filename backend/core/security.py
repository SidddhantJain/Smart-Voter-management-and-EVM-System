from __future__ import annotations

from datetime import datetime, timedelta
import os
from typing import Any

from passlib.context import CryptContext
import jwt

from backend.core.config import get_config

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
config = get_config()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: Any, expires_delta: int | None = None) -> str:
    secret = os.getenv("JWT_SECRET", getattr(config, "jwt_secret", "change-me"))
    algorithm = os.getenv("JWT_ALGORITHM", getattr(config, "jwt_algorithm", "HS256"))
    expire = datetime.utcnow() + (timedelta(seconds=expires_delta) if expires_delta else timedelta(minutes=60))
    to_encode = {"sub": str(subject), "exp": expire}
    encoded = jwt.encode(to_encode, secret, algorithm=algorithm)
    return encoded


def decode_access_token(token: str) -> dict:
    secret = os.getenv("JWT_SECRET", getattr(config, "jwt_secret", "change-me"))
    algorithm = os.getenv("JWT_ALGORITHM", getattr(config, "jwt_algorithm", "HS256"))
    return jwt.decode(token, secret, algorithms=[algorithm])
