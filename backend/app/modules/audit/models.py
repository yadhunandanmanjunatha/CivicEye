"""Append-only history tables (UPDATE/DELETE blocked by a database trigger) and the event log."""
from datetime import datetime

from sqlalchemy import BigInteger, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.types import JSON, created_ts
from app.db import Base


class StatusEvent(Base):
    __tablename__ = "status_events"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    object_type: Mapped[str] = mapped_column(String(8))  # SR | WO
    object_id: Mapped[str] = mapped_column(String(20), index=True)
    from_state: Mapped[str | None] = mapped_column(String(16))
    to_state: Mapped[str] = mapped_column(String(16))
    actor_type: Mapped[str] = mapped_column(String(8))
    actor: Mapped[str] = mapped_column(String(80))  # user id, agent name or "system"
    reason: Mapped[str | None] = mapped_column(Text)
    remarks: Mapped[str | None] = mapped_column(Text)  # plain-language text shown to citizens
    at: Mapped[datetime] = created_ts()


class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    actor: Mapped[str] = mapped_column(String(80))
    actor_type: Mapped[str] = mapped_column(String(8))
    action: Mapped[str] = mapped_column(String(60))
    object_type: Mapped[str] = mapped_column(String(24))
    object_id: Mapped[str] = mapped_column(String(40), index=True)
    before_json: Mapped[dict | None] = mapped_column(JSON)
    after_json: Mapped[dict | None] = mapped_column(JSON)
    at: Mapped[datetime] = created_ts()


class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(40), index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    at: Mapped[datetime] = created_ts()
    handled: Mapped[int] = mapped_column(Integer, default=0)
