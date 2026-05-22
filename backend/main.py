from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.db import init_db
from backend.core.config import get_config
from backend.modules.analytics.router import router as analytics_router
from backend.modules.auth.router import router as auth_router
from backend.modules.constituencies.router import router as constituencies_router
from backend.modules.graph.router import router as graph_router
from backend.modules.governance.router import router as governance_router
from backend.modules.voters.router import router as voters_router


config = get_config()
app = FastAPI(title=config.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()


app.include_router(auth_router, prefix=config.api_prefix)
app.include_router(voters_router, prefix=config.api_prefix)
app.include_router(constituencies_router, prefix=config.api_prefix)
app.include_router(graph_router, prefix=config.api_prefix)
app.include_router(analytics_router, prefix=config.api_prefix)
app.include_router(governance_router, prefix=config.api_prefix)


@app.get("/")
def root() -> dict:
    return {
        "status": "ok",
        "service": config.app_name,
        "environment": config.environment,
        "modules": ["auth", "voters", "constituencies", "graph", "analytics", "governance"],
    }


@app.get("/health")
def health() -> dict:
    return {"status": "healthy"}
