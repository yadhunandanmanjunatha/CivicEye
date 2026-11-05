"""Test fixtures. Tests use the civicflow_test database, rebuilt from migrations once per session."""
import os

from app.config import get_settings

# Point the app at the test database BEFORE app.db creates its engine.
os.environ["DATABASE_URL"] = get_settings().test_database_url
os.environ.setdefault("AGENT_MODE", "rules")
os.environ.setdefault("SCHEDULER_ENABLED", "false")
get_settings.cache_clear()

import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from pathlib import Path  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.db import SessionLocal, engine  # noqa: E402

BACKEND = Path(__file__).resolve().parents[1]
# Tables never truncated between tests (reference data seeded by fixtures stays explicit anyway).
_KEEP = {"alembic_version", "spatial_ref_sys"}


def _alembic_cfg() -> Config:
    cfg = Config(str(BACKEND / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND / "alembic"))
    return cfg


@pytest.fixture(scope="session", autouse=True)
def _migrated_db():
    url = os.environ["DATABASE_URL"]
    cfg = _alembic_cfg()
    cfg.cmd_opts = type("o", (), {"x": [f"url={url}"]})()
    with engine.begin() as c:
        c.execute(text("DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;"))
    command.upgrade(cfg, "head")
    yield


@pytest.fixture()
def db():
    """A session on a clean database (all app tables truncated before each test)."""
    with engine.begin() as c:
        tables = [r[0] for r in c.execute(text(
            "select tablename from pg_tables where schemaname='public'"))]
        tables = [t for t in tables if t not in _KEEP]
        # Triggers block DELETE but not TRUNCATE (TRUNCATE is a separate privilege); fine for tests.
        c.execute(text("TRUNCATE " + ", ".join(f'"{t}"' for t in tables) + " RESTART IDENTITY CASCADE"))
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()
