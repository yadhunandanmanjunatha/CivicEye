"""Service requests (complaints), their reporters, attachments and feedback."""
from datetime import datetime, timedelta
import uuid

from sqlalchemy import BigInteger, Float, ForeignKey, Integer, Interval, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.types import created_ts, enum_col, point, ts
from app.db import Base


class ServiceRequest(Base):
    __tablename__ = "service_requests"
    id: Mapped[str] = mapped_column(String(20), primary_key=True)  # SR-2026-000123
    tracking_code: Mapped[str] = mapped_column(String(12), unique=True)
    category: Mapped[str] = enum_col(24, index=True)
    description: Mapped[str] = mapped_column(Text)
    location = point(nullable=False)
    address: Mapped[str | None] = mapped_column(String(300))
    landmark: Mapped[str | None] = mapped_column(String(200))
    ward_id: Mapped[str | None] = mapped_column(ForeignKey("wards.id"), index=True)
    department_id: Mapped[str | None] = mapped_column(ForeignKey("departments.id"))
    asset_id: Mapped[str | None] = mapped_column(ForeignKey("assets.id"))
    status: Mapped[str] = enum_col(16, index=True)
    status_before_hold: Mapped[str | None] = mapped_column(String(16))
    priority: Mapped[str] = enum_col(2, default="P3")
    priority_score: Mapped[float] = mapped_column(Float, default=0)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), index=True)
    parent_sr_id: Mapped[str | None] = mapped_column(ForeignKey("service_requests.id"))
    reporter_count: Mapped[int] = mapped_column(Integer, default=1)
    source: Mapped[str] = enum_col(16, default="CITIZEN_WEB")
    incident_id: Mapped[str | None] = mapped_column(ForeignKey("incidents.id"))
    escalation_level: Mapped[int] = mapped_column(Integer, default=0)
    reopen_count: Mapped[int] = mapped_column(Integer, default=0)
    sla_policy_id: Mapped[int | None] = mapped_column(ForeignKey("sla_policies.id"))
    sla_started_at: Mapped[datetime | None] = ts()
    sla_due_at: Mapped[datetime | None] = ts()
    sla_paused_total: Mapped[timedelta] = mapped_column(Interval, default=timedelta(0))
    sla_paused_since: Mapped[datetime | None] = ts()
    sla_state_cached: Mapped[str | None] = mapped_column(String(10))  # last state seen by the scanner
    closure_type: Mapped[str | None] = mapped_column(String(8))
    citizen_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    language: Mapped[str] = mapped_column(String(2), default="en")
    corroboration_count: Mapped[int] = mapped_column(Integer, default=0)  # distinct vehicles (Agent 3)
    resolved_at: Mapped[datetime | None] = ts()
    closed_at: Mapped[datetime | None] = ts()
    created_at: Mapped[datetime] = created_ts()


class SrReporter(Base):
    """Everyone who reported the same issue keeps getting updates, including merged reporters."""
    __tablename__ = "sr_reporters"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sr_id: Mapped[str] = mapped_column(ForeignKey("service_requests.id"), index=True)
    citizen_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    contact_name: Mapped[str | None] = mapped_column(String(120))
    contact_mobile: Mapped[str | None] = mapped_column(String(15))
    language: Mapped[str] = mapped_column(String(2), default="en")
    merged_from_sr_id: Mapped[str | None] = mapped_column(String(20))
    created_at: Mapped[datetime] = created_ts()


class Attachment(Base):
    __tablename__ = "attachments"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sr_id: Mapped[str | None] = mapped_column(ForeignKey("service_requests.id"), index=True)
    wo_id: Mapped[str | None] = mapped_column(ForeignKey("work_orders.id"), index=True)
    kind: Mapped[str] = enum_col(8)
    path: Mapped[str] = mapped_column(String(300))
    mime: Mapped[str] = mapped_column(String(40), default="image/jpeg")
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    phash: Mapped[str | None] = mapped_column(String(32))
    phash_int: Mapped[int | None] = mapped_column(BigInteger)
    exif_lat: Mapped[float | None] = mapped_column(Float)
    exif_lon: Mapped[float | None] = mapped_column(Float)
    exif_time: Mapped[datetime | None] = ts()
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    uploaded_at: Mapped[datetime] = created_ts()


class Feedback(Base):
    __tablename__ = "feedback"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sr_id: Mapped[str] = mapped_column(ForeignKey("service_requests.id"), index=True)
    rating: Mapped[int | None] = mapped_column(Integer)
    comment: Mapped[str | None] = mapped_column(Text)
    reopen_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = created_ts()
