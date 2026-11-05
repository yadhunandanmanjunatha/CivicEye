"""Connected-vehicle data collection: sources, raw detections, dead-letter, clusters, review queue."""
from datetime import datetime
import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.types import JSON, created_ts, enum_col, point, ts
from app.db import Base


class DataSource(Base):
    __tablename__ = "data_sources"
    id: Mapped[str] = mapped_column(String(24), primary_key=True)  # "oem-sim"
    name: Mapped[str] = mapped_column(String(120))
    kind: Mapped[str] = mapped_column(String(16))  # VEHICLE | WEATHER
    api_key_hash: Mapped[str] = mapped_column(String(64))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_ingest_at: Mapped[datetime | None] = ts()


class RawDetection(Base):
    __tablename__ = "raw_detections"
    __table_args__ = (UniqueConstraint("source_id", "source_record_id"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("data_sources.id"))
    source_record_id: Mapped[str] = mapped_column(String(80))
    location = point(nullable=False)
    hazard_type: Mapped[str] = enum_col(16)
    detected_at: Mapped[datetime] = ts(nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    speed_kmph: Mapped[float | None] = mapped_column(Float)
    vertical_accel_peak_g: Mapped[float | None] = mapped_column(Float)
    vehicle_ref: Mapped[str] = mapped_column(String(80), index=True)
    image_url: Mapped[str | None] = mapped_column(String(300))
    raw_payload: Mapped[dict] = mapped_column(JSON)
    cluster_id: Mapped[int | None] = mapped_column(ForeignKey("hazard_clusters.id"), index=True)
    ingested_at: Mapped[datetime] = created_ts()


class RejectedDetection(Base):
    __tablename__ = "rejected_detections"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("data_sources.id"), index=True)
    source_record_id: Mapped[str | None] = mapped_column(String(80))
    reason: Mapped[str] = mapped_column(String(24))
    detail: Mapped[str | None] = mapped_column(Text)
    raw_payload: Mapped[dict] = mapped_column(JSON)
    at: Mapped[datetime] = created_ts()


class IngestRequest(Base):
    """Idempotency-Key replay protection for the ingestion API."""
    __tablename__ = "ingest_requests"
    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    source_id: Mapped[str] = mapped_column(String(24))
    response: Mapped[dict] = mapped_column(JSON)
    at: Mapped[datetime] = created_ts()


class HazardCluster(Base):
    __tablename__ = "hazard_clusters"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    centre = point(nullable=False)
    hazard_type: Mapped[str] = enum_col(16)
    detection_count: Mapped[int] = mapped_column(Integer, default=0)
    distinct_vehicles: Mapped[int] = mapped_column(Integer, default=0)
    days_seen: Mapped[int] = mapped_column(Integer, default=0)
    avg_confidence: Mapped[float] = mapped_column(Float, default=0)
    avg_jolt_g: Mapped[float | None] = mapped_column(Float)
    first_seen: Mapped[datetime | None] = ts()
    last_seen: Mapped[datetime | None] = ts()
    status: Mapped[str] = mapped_column(String(12), default="NEW")  # NEW | ACTIONED | DISMISSED | REVIEW
    decision: Mapped[str | None] = mapped_column(String(16))
    decision_reason: Mapped[str | None] = mapped_column(Text)
    linked_sr_id: Mapped[str | None] = mapped_column(ForeignKey("service_requests.id"))
    linked_wo_id: Mapped[str | None] = mapped_column(ForeignKey("work_orders.id"))
    reviewed_count: Mapped[int] = mapped_column(Integer, default=0)  # detection_count at last review
    updated_at: Mapped[datetime] = created_ts()


class ReviewItem(Base):
    __tablename__ = "review_queue"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cluster_id: Mapped[int] = mapped_column(ForeignKey("hazard_clusters.id"), index=True)
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(10), default="OPEN")
    agent_run_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("agent_runs.id"))
    decided_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    decision: Mapped[str | None] = mapped_column(String(10))
    decision_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = created_ts()
