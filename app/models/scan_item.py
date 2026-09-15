import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def utcnow(): return datetime.now(timezone.utc)


class ScanItem(Base):
    __tablename__ = 'scan_items'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id: Mapped[str] = mapped_column(ForeignKey('scan_batches.id', ondelete='CASCADE'), index=True)
    item_number: Mapped[int] = mapped_column(Integer)
    original_filename: Mapped[str] = mapped_column(String(255))
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32), default='QUEUED', index=True)
    failure_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    failure_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    original_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    optimized_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    image_width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    image_height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quality_metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    thumbnail_mime: Mapped[str | None] = mapped_column(String(50), nullable=True)
    thumbnail_data: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    current_attempt_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    exported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    batch = relationship('ScanBatch', back_populates='items')
    attempts = relationship('ScanAttempt', back_populates='scan_item', cascade='all, delete-orphan')
    kk_record = relationship('KKRecord', back_populates='scan_item', cascade='all, delete-orphan', uselist=False)
    issues = relationship('ScanIssue', back_populates='scan_item', cascade='all, delete-orphan')
