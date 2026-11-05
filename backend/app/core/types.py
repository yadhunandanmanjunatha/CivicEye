"""Column helpers shared by all models."""
from datetime import datetime, timezone
import uuid

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import mapped_column


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def pk_uuid():
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


def ts(nullable: bool = True, default=None):
    return mapped_column(DateTime(timezone=True), nullable=nullable, default=default)


def created_ts():
    return mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


def point(nullable: bool = True):
    return mapped_column(Geometry("POINT", srid=4326, spatial_index=True), nullable=nullable)


def geom(kind: str, nullable: bool = True):
    return mapped_column(Geometry(kind, srid=4326, spatial_index=True), nullable=nullable)


def enum_col(length: int = 32, nullable: bool = False, default=None, index: bool = False):
    return mapped_column(String(length), nullable=nullable, default=default, index=index)


JSON = JSONB
