from __future__ import annotations

from importlib import reload
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def test_sqlalchemy_session_persists_new_models(tmp_path, monkeypatch):
    database_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path.as_posix()}")
    monkeypatch.setenv("POSTGIS_ENABLED", "false")
    monkeypatch.setenv("DATABASE_BACKEND", "sqlite")

    import backend.core.config as config_module
    import backend.core.db as db_module
    import backend.core.models as models_module

    reload(config_module)
    reload(db_module)
    reload(models_module)

    db_module.init_db()

    session = db_module.SessionLocal()
    try:
        session.add(models_module.Voter(voter_id="V100", first_name="Ada", last_name="Lovelace", constituency="C1"))
        session.add(models_module.Constituency(constituency_id="C1", name="Central", state="State-1", district="District-9"))
        session.add(models_module.GraphNode(id="N1", label="Polling Station", kind="location"))
        session.add(models_module.GraphEdge(source="N1", target="C1", relation="belongs_to"))
        session.add(models_module.AnalyticsEvent(event_type="test_event", payload={"ok": True}))
        session.commit()

        assert session.query(models_module.Voter).count() == 1
        assert session.query(models_module.Constituency).count() == 1
        assert session.query(models_module.GraphNode).count() == 1
        assert session.query(models_module.GraphEdge).count() == 1
        assert session.query(models_module.AnalyticsEvent).count() == 1
    finally:
        session.close()


def test_database_settings_expose_postgis_flags(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg2://user:pass@localhost:5432/voteguard")
    monkeypatch.setenv("DATABASE_BACKEND", "postgresql")
    monkeypatch.setenv("POSTGIS_ENABLED", "true")
    monkeypatch.setenv("POSTGIS_SRID", "3857")

    import backend.core.config as config_module
    import backend.core.db as db_module

    reload(config_module)
    reload(db_module)

    assert db_module.DATABASE_URL.startswith("postgresql+")
    assert db_module.DATABASE_BACKEND == "postgresql"
    assert db_module.POSTGIS_ENABLED is True
    assert db_module.POSTGIS_SRID == 3857
