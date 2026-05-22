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


def get_config() -> AppConfig:
    return AppConfig()
