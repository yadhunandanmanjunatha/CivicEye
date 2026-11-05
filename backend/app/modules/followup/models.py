"""Inter-agency referrals and escalations."""
from datetime import datetime
import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.types import JSON, created_ts, enum_col, ts
from app.db import Base


class Referral(Base):
    __tablename__ = "referrals"
    id: Mapped[str] = mapped_column(String(20), primary_key=True)  # REF-2026-000012
    sr_id: Mapped[str] = mapped_column(ForeignKey("service_requests.id"), index=True)
    agency: Mapped[str] = enum_col(8, index=True)
    reason: Mapped[str] = mapped_column(Text)
    sent_at: Mapped[datetime] = created_ts()
    followups_sent: Mapped[int] = mapped_column(Integer, default=0)
    last_followup_at: Mapped[datetime | None] = ts()
    agency_status: Mapped[str] = enum_col(14, default="PENDING")
    agency_reply: Mapped[str | None] = mapped_column(Text)
    replied_at: Mapped[datetime | None] = ts()
    replied_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    messages: Mapped[list] = mapped_column(JSON, default=list)  # [{at, from, text}]


class Escalation(Base):
    __tablename__ = "escalations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sr_id: Mapped[str] = mapped_column(ForeignKey("service_requests.id"), index=True)
    level: Mapped[int] = mapped_column(Integer)
    trigger: Mapped[str] = mapped_column(String(24))  # SLA_BREACH | AGENCY_NO_RESPONSE | REOPEN
    reason_summary: Mapped[str] = mapped_column(Text)
    authority_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    agent_run_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("agent_runs.id"))
    created_at: Mapped[datetime] = created_ts()
    deadline: Mapped[datetime | None] = ts()
