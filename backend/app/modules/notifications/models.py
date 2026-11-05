from datetime import datetime
import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.types import created_ts
from app.db import Base


class Notification(Base):
    """Outbox. Channel IN_APP is delivered on My Notifications and the Track page."""
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipient_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), index=True)
    recipient_contact: Mapped[str | None] = mapped_column(String(15))
    channel: Mapped[str] = mapped_column(String(10), default="IN_APP")
    language: Mapped[str] = mapped_column(String(2), default="en")
    event: Mapped[str] = mapped_column(String(40))
    title: Mapped[str] = mapped_column(String(160))
    body: Mapped[str] = mapped_column(Text)
    related_sr_id: Mapped[str | None] = mapped_column(ForeignKey("service_requests.id"), index=True)
    sent_by: Mapped[str] = mapped_column(String(40), default="SYSTEM")  # agent name or SYSTEM
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = created_ts()
