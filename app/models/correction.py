import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


def utcnow(): return datetime.now(timezone.utc)


class FieldCorrection(Base):
    __tablename__ = 'field_corrections'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_item_id: Mapped[str] = mapped_column(ForeignKey('scan_items.id', ondelete='CASCADE'), index=True)
    member_id: Mapped[str | None] = mapped_column(ForeignKey('kk_members.id', ondelete='CASCADE'), nullable=True)
    field_name: Mapped[str] = mapped_column(String(100))
    original_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    corrected_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
