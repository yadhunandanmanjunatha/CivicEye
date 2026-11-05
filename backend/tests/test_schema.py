import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.modules.audit.models import AuditLog, StatusEvent


def test_all_model_tables_exist(db):
    from app.models import metadata
    existing = {r[0] for r in db.execute(text("select tablename from pg_tables where schemaname='public'"))}
    assert set(metadata.tables) <= existing


@pytest.mark.parametrize("model,kwargs", [
    (AuditLog, dict(actor="u", actor_type="HUMAN", action="x", object_type="SR", object_id="SR-1")),
    (StatusEvent, dict(object_type="SR", object_id="SR-1", to_state="SUBMITTED", actor_type="SYSTEM",
                       actor="system")),
])
def test_history_tables_are_append_only(db, model, kwargs):
    row = model(**kwargs)
    db.add(row)
    db.commit()
    with pytest.raises(DBAPIError, match="append-only"):
        db.execute(text(f"UPDATE {model.__tablename__} SET object_id='SR-2'"))
    db.rollback()
    with pytest.raises(DBAPIError, match="append-only"):
        db.execute(text(f"DELETE FROM {model.__tablename__}"))
    db.rollback()


def test_postgis_and_trgm_available(db):
    assert db.execute(text("select ST_Distance('POINT(77.48 12.90)'::geography,"
                           " 'POINT(77.49 12.90)'::geography)")).scalar() > 1000
    assert db.execute(text("select similarity('pothole near school', 'pothole near the school')")).scalar() > 0.5
