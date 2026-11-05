"""Surge incidents and weather alerts."""
from datetime import datetime
import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.types import created_ts, enum_col, geom, point, ts
from app.db import Base


class Incident(Base):
    __tablename__ = "incidents"
    id: Mapped[str] = mapped_column(String(20), primary_key=True)  # INC-2026-0001
    name: Mapped[str] = mapped_column(String(160))
    area = geom("GEOMETRY")
    centre = point()
    severity: Mapped[str] = mapped_column(String(8))  # LOW | MEDIUM | HIGH
    status: Mapped[str] = mapped_column(String(10), default="ACTIVE")
    suggested_resources: Mapped[str | None] = mapped_column(Text)
    advisory_draft_en: Mapped[str | None] = mapped_column(Text)
    advisory_draft_kn: Mapped[str | None] = mapped_column(Text)
    advisory_published: Mapped[bool] = mapped_column(Boolean, default=False)
    advisory_text_en: Mapped[str | None] = mapped_column(Text)
    advisory_text_kn: Mapped[str | None] = mapped_column(Text)
    published_at: Mapped[datetime | None] = ts()
    published_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    summary: Mapped[str | None] = mapped_column(Text)
    summary_at: Mapped[datetime | None] = ts()
    created_at: Mapped[datetime] = created_ts()


class WeatherAlert(Base):
    __tablename__ = "weather_alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(24))  # OPEN_METEO | INGEST
    source_alert_id: Mapped[str] = mapped_column(String(80), unique=True)
    area_name: Mapped[str] = mapped_column(String(120))
    location = point()
    radius_km: Mapped[float] = mapped_column(Float, default=5)
    severity: Mapped[str] = enum_col(8)
    kind: Mapped[str] = mapped_column(String(20), default="HEAVY_RAIN")
    valid_from: Mapped[datetime] = ts(nullable=False)
    valid_to: Mapped[datetime] = ts(nullable=False)
    created_at: Mapped[datetime] = created_ts()
    precipitation_mm: Mapped[float | None] = mapped_column(Float)
    surge_checked: Mapped[int] = mapped_column(Integer, default=0)
