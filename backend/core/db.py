from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.core.config import get_config


config = get_config()
DATABASE_URL = config.database_url
DATABASE_BACKEND = config.database_backend
POSTGIS_ENABLED = config.postgis_enabled
POSTGIS_SRID = config.postgis_srid
GEOJSON_SUPPORT = config.geojson_support

engine_kwargs = {"future": True}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from backend.core.models import Base

    Base.metadata.create_all(bind=engine)


