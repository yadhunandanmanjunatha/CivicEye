from datetime import datetime
import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.types import created_ts, enum_col, pk_uuid, ts
from app.db import Base


class User(Base):
    """Citizens register themselves; staff (officer/field/control/agency) are created by Control Room."""
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = pk_uuid()
    name: Mapped[str] = mapped_column(String(120))
    mobile: Mapped[str | None] = mapped_column(String(15), unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(100))  # None = cannot log in (historical)
    role: Mapped[str] = enum_col(index=True)
    designation: Mapped[str | None] = mapped_column(String(80))  # e.g. "Assistant Engineer"
    escalation_level: Mapped[int | None] = mapped_column(Integer)  # 1..4 for escalation authorities
    ward_id: Mapped[str | None] = mapped_column(ForeignKey("wards.id"), index=True)
    zone: Mapped[str | None] = mapped_column(String(60))
    department_id: Mapped[str | None] = mapped_column(ForeignKey("departments.id"))
    crew_id: Mapped[str | None] = mapped_column(ForeignKey("crews.id"))
    agency: Mapped[str | None] = mapped_column(String(16))
    office_phone: Mapped[str | None] = mapped_column(String(20))
    language: Mapped[str] = mapped_column(String(2), default="en")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    failed_logins: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = ts()
    created_at: Mapped[datetime] = created_ts()


class Captcha(Base):
    __tablename__ = "captchas"
    id: Mapped[uuid.UUID] = pk_uuid()
    question: Mapped[str] = mapped_column(String(40))
    answer: Mapped[int] = mapped_column(Integer)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = ts(nullable=False)


class Visit(Base):
    __tablename__ = "visits"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_key: Mapped[str] = mapped_column(String(64), unique=True)
    at: Mapped[datetime] = created_ts()
