import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def utcnow(): return datetime.now(timezone.utc)


class Export(Base):
    __tablename__ = 'exports'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    export_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    filter_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    kk_count: Mapped[int] = mapped_column(Integer, default=0)
    filename: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    items = relationship('ExportItem', back_populates='export', cascade='all, delete-orphan')


class ExportItem(Base):
    __tablename__ = 'export_items'
    export_id: Mapped[str] = mapped_column(ForeignKey('exports.id', ondelete='CASCADE'), primary_key=True)
    scan_item_id: Mapped[str] = mapped_column(ForeignKey('scan_items.id', ondelete='CASCADE'), primary_key=True)
    export = relationship('Export', back_populates='items')
