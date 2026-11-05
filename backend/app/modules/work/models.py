"""Crews, work orders, inventory, material requests and reassignment proposals."""
from datetime import datetime
import uuid

from sqlalchemy import ARRAY, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.types import JSON, created_ts, enum_col, point, ts
from app.db import Base


class Crew(Base):
    __tablename__ = "crews"
    id: Mapped[str] = mapped_column(String(12), primary_key=True)  # "W12-A"
    name: Mapped[str] = mapped_column(String(80))
    ward_id: Mapped[str] = mapped_column(ForeignKey("wards.id"), index=True)
    skills: Mapped[list[str]] = mapped_column(ARRAY(String(20)), default=list)
    capacity: Mapped[int] = mapped_column(Integer, default=4)
    base_location = point()
    audit_priority: Mapped[int] = mapped_column(Integer, default=0)  # raised by repeated FLAGs


class WorkOrder(Base):
    __tablename__ = "work_orders"
    id: Mapped[str] = mapped_column(String(20), primary_key=True)  # WO-2026-000040
    sr_id: Mapped[str] = mapped_column(ForeignKey("service_requests.id"), index=True)
    crew_id: Mapped[str] = mapped_column(ForeignKey("crews.id"), index=True)
    asset_id: Mapped[str | None] = mapped_column(ForeignKey("assets.id"))
    scope: Mapped[str] = mapped_column(Text)
    root_cause: Mapped[str | None] = mapped_column(Text)
    est_cost_inr: Mapped[float | None] = mapped_column(Float)
    status: Mapped[str] = enum_col(12, index=True)
    status_before_hold: Mapped[str | None] = mapped_column(String(12))
    rework_reason: Mapped[str | None] = mapped_column(Text)
    quality_flag: Mapped[str | None] = mapped_column(Text)  # set when a repair may have failed
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    assigned_at: Mapped[datetime] = created_ts()
    started_at: Mapped[datetime | None] = ts()
    completed_at: Mapped[datetime | None] = ts()
    verified_at: Mapped[datetime | None] = ts()
    verified_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    audit_verdict: Mapped[str | None] = mapped_column(String(4))
    audit_score: Mapped[int | None] = mapped_column(Integer)
    audit_run_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("agent_runs.id"))


class InventoryItem(Base):
    __tablename__ = "inventory"
    item: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    unit: Mapped[str] = mapped_column(String(12))
    qty: Mapped[float] = mapped_column(Float, default=0)
    out_of_stock_since: Mapped[datetime | None] = ts()


class MaterialRequest(Base):
    __tablename__ = "material_requests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item: Mapped[str] = mapped_column(ForeignKey("inventory.item"))
    qty: Mapped[float] = mapped_column(Float)
    sr_id: Mapped[str | None] = mapped_column(ForeignKey("service_requests.id"))
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(12), default="OPEN")
    raised_by: Mapped[str] = mapped_column(String(60))  # agent name or user id
    created_at: Mapped[datetime] = created_ts()


class ReassignmentProposal(Base):
    __tablename__ = "reassignment_proposals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    wo_id: Mapped[str] = mapped_column(ForeignKey("work_orders.id"), index=True)
    from_crew_id: Mapped[str] = mapped_column(ForeignKey("crews.id"))
    to_crew_id: Mapped[str] = mapped_column(ForeignKey("crews.id"))
    reason: Mapped[str] = mapped_column(Text)
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = enum_col(10, default="PENDING")
    agent_run_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("agent_runs.id"))
    decided_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    decision_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = created_ts()
    decided_at: Mapped[datetime | None] = ts()
