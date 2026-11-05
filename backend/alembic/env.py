"""Alembic environment. Uses DATABASE_URL from settings (override with -x url=...)."""
from alembic import context
from geoalchemy2 import alembic_helpers
from sqlalchemy import create_engine

from app.config import get_settings
from app.models import metadata

config = context.config


def _include(obj, name, type_, reflected, compare_to):
    # Only manage our own tables (PostGIS adds tiger/topology tables we must not touch).
    if type_ == "table" and reflected and compare_to is None:
        return False
    return alembic_helpers.include_object(obj, name, type_, reflected, compare_to)


def run_migrations_online() -> None:
    url = context.get_x_argument(as_dictionary=True).get("url") or get_settings().database_url
    engine = create_engine(url)
    with engine.connect() as conn:
        context.configure(
            connection=conn,
            target_metadata=metadata,
            include_object=_include,
            process_revision_directives=alembic_helpers.writer,
            render_item=alembic_helpers.render_item,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
