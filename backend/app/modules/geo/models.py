"""City geography and reference data: wards, departments, assets, places, roads, planned works."""
from datetime import date, datetime

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.types import created_ts, enum_col, geom, point
from app.db import Base


class Ward(Base):
    __tablename__ = "wards"
    id: Mapped[str] = mapped_column(String(8), primary_key=True)  # "W12"
    name: Mapped[str] = mapped_column(String(80))
    name_kn: Mapped[str | None] = mapped_column(String(120))
    zone: Mapped[str] = mapped_column(String(60))
    geom = geom("MULTIPOLYGON")


class Department(Base):
    __tablename__ = "departments"
    id: Mapped[str] = mapped_column(String(16), primary_key=True)  # "ROADS"
    name: Mapped[str] = mapped_column(String(80))
    name_kn: Mapped[str | None] = mapped_column(String(120))


class Asset(Base):
    __tablename__ = "assets"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)  # "STREETLIGHT-W12-00871"
    type: Mapped[str] = mapped_column(String(24), index=True)  # STREETLIGHT | MANHOLE | DRAIN | ROAD
    ward_id: Mapped[str | None] = mapped_column(ForeignKey("wards.id"))
    owner: Mapped[str] = enum_col(16)
    condition: Mapped[str] = mapped_column(String(16), default="OK")
    location = point(nullable=False)
    description: Mapped[str | None] = mapped_column(String(200))


class AssetEvent(Base):
    __tablename__ = "asset_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.id"), index=True)
    type: Mapped[str] = mapped_column(String(16))  # COMPLAINT | REPAIR | FAILURE
    date: Mapped[date] = mapped_column(Date)
    note: Mapped[str | None] = mapped_column(Text)
    sr_id: Mapped[str | None] = mapped_column(String(20))


class PlannedWork(Base):
    __tablename__ = "planned_works"
    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    agency: Mapped[str] = mapped_column(String(40))
    geom = geom("GEOMETRY", nullable=False)
    start: Mapped[date] = mapped_column(Date)
    end: Mapped[date] = mapped_column(Date)


class SensitivePlace(Base):
    __tablename__ = "sensitive_places"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    type: Mapped[str] = mapped_column(String(24))  # SCHOOL | HOSPITAL | MARKET | BUS_STAND
    location = point(nullable=False)


class KnownRoadFeature(Base):
    __tablename__ = "known_road_features"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = enum_col(20)
    name: Mapped[str | None] = mapped_column(String(120))
    location = point(nullable=False)


class RoadSegment(Base):
    __tablename__ = "road_segments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    road_class: Mapped[str] = enum_col(12)
    geom = geom("LINESTRING", nullable=False)


class SlaPolicy(Base):
    __tablename__ = "sla_policies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = enum_col(24)
    priority: Mapped[str] = enum_col(2)
    resolution_hours: Mapped[int] = mapped_column(Integer)
    verification_window_hours: Mapped[int] = mapped_column(Integer, default=168)
    duplicate_radius_m: Mapped[int] = mapped_column(Integer, default=50)
    created_at: Mapped[datetime] = created_ts()
