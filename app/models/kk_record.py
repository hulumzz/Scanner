import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def utcnow(): return datetime.now(timezone.utc)


class KKRecord(Base):
    __tablename__ = 'kk_records'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_item_id: Mapped[str] = mapped_column(ForeignKey('scan_items.id', ondelete='CASCADE'), unique=True, index=True)
    no_kk: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    nama_kepala_keluarga: Mapped[str | None] = mapped_column(String(255), nullable=True)
    alamat: Mapped[str | None] = mapped_column(String(500), nullable=True)
    rt: Mapped[str | None] = mapped_column(String(8), nullable=True)
    rw: Mapped[str | None] = mapped_column(String(8), nullable=True)
    kode_pos: Mapped[str | None] = mapped_column(String(12), nullable=True)
    dusun: Mapped[str | None] = mapped_column(String(255), nullable=True)
    desa: Mapped[str | None] = mapped_column(String(255), nullable=True)
    kecamatan: Mapped[str | None] = mapped_column(String(255), nullable=True)
    kabupaten: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provinsi: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    scan_item = relationship('ScanItem', back_populates='kk_record')
    members = relationship('KKMember', back_populates='kk_record', cascade='all, delete-orphan', order_by='KKMember.no_urut_kk')
