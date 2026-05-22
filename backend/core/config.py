from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AppConfig:
    app_name: str = "VoteGuard Nexus API"
    environment: str = os.getenv("VOTEGUARD_ENV", "development")
    api_prefix: str = "/api/v1"
    host: str = os.getenv("VOTEGUARD_BACKEND_HOST", "127.0.0.1")
    port: int = int(os.getenv("VOTEGUARD_BACKEND_PORT", "8000"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./voteguard_nexus.db")
    database_backend: str = os.getenv("DATABASE_BACKEND", "sqlite")
    postgis_enabled: bool = os.getenv("POSTGIS_ENABLED", "false").lower() in {"1", "true", "yes", "on"}
    postgis_srid: int = int(os.getenv("POSTGIS_SRID", "4326"))
    geojson_support: bool = os.getenv("GEOJSON_SUPPORT", "true").lower() in {"1", "true", "yes", "on"}
    jwt_secret: str = os.getenv("JWT_SECRET", "change-this-secret-in-prod")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_access_token_expires_seconds: int = int(os.getenv("JWT_ACCESS_EXPIRES", str(60 * 60)))


def get_config() -> AppConfig:
    return AppConfig()
