"""Agent decision log: one agent_runs row per run, one agent_steps row per tool call."""
from datetime import datetime
import uuid

from sqlalchemy import Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.types import JSON, created_ts, pk_uuid, ts
from app.db import Base


class AgentRun(Base):
    __tablename__ = "agent_runs"
    __table_args__ = (UniqueConstraint("agent", "idempotency_key"),)
    id: Mapped[uuid.UUID] = pk_uuid()
    agent: Mapped[str] = mapped_column(String(32), index=True)
    trigger: Mapped[str] = mapped_column(String(60))
    idempotency_key: Mapped[str] = mapped_column(String(120))
    subject_type: Mapped[str | None] = mapped_column(String(8))
    subject_id: Mapped[str | None] = mapped_column(String(40), index=True)
    input_summary: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(10), default="RUNNING")
    model: Mapped[str | None] = mapped_column(String(80))  # "provider:model" or "rules"
    fallback_reason: Mapped[str | None] = mapped_column(Text)
    output: Mapped[dict | None] = mapped_column(JSON)
    decision_summary: Mapped[str | None] = mapped_column(String(300))
    rationale: Mapped[list | None] = mapped_column(JSON)
    confidence: Mapped[float | None] = mapped_column(Float)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    tokens_in: Mapped[int | None] = mapped_column(Integer)
    tokens_out: Mapped[int | None] = mapped_column(Integer)
    overridden_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    override_reason: Mapped[str | None] = mapped_column(Text)
    accepted_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    started_at: Mapped[datetime] = created_ts()
    finished_at: Mapped[datetime | None] = ts()


class AgentStep(Base):
    __tablename__ = "agent_steps"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_runs.id"), index=True)
    seq: Mapped[int] = mapped_column(Integer)
    tool: Mapped[str] = mapped_column(String(60))
    args: Mapped[dict] = mapped_column(JSON, default=dict)
    result_summary: Mapped[dict | list | None] = mapped_column(JSON)
    ok: Mapped[bool] = mapped_column(default=True)
    error: Mapped[str | None] = mapped_column(Text)
    ms: Mapped[int] = mapped_column(Integer, default=0)
    at: Mapped[datetime] = created_ts()
