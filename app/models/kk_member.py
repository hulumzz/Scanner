import uuid
from datetime import date, datetime, timezone
from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def utcnow(): return datetime.now(timezone.utc)


class KKMember(Base):
    __tablename__ = 'kk_members'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    kk_record_id: Mapped[str] = mapped_column(ForeignKey('kk_records.id', ondelete='CASCADE'), index=True)
    no_urut_kk: Mapped[int] = mapped_column(Integer)
    status_hubungan: Mapped[str | None] = mapped_column(String(100), nullable=True)
    nik: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    nama_lengkap: Mapped[str | None] = mapped_column(String(255), nullable=True)
    jenis_kelamin: Mapped[str | None] = mapped_column(String(30), nullable=True)
    tempat_lahir: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tanggal_lahir: Mapped[date | None] = mapped_column(Date, nullable=True)
    agama: Mapped[str | None] = mapped_column(String(50), nullable=True)
    pendidikan: Mapped[str | None] = mapped_column(String(150), nullable=True)
    jenis_pekerjaan: Mapped[str | None] = mapped_column(String(150), nullable=True)
    status_perkawinan: Mapped[str | None] = mapped_column(String(80), nullable=True)
    kewarganegaraan: Mapped[str | None] = mapped_column(String(40), nullable=True)
    no_paspor: Mapped[str | None] = mapped_column(String(50), nullable=True)
    no_kitas_kitap: Mapped[str | None] = mapped_column(String(50), nullable=True)
    nama_ayah: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nama_ibu: Mapped[str | None] = mapped_column(String(255), nullable=True)
    golongan_darah: Mapped[str | None] = mapped_column(String(8), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    kk_record = relationship('KKRecord', back_populates='members')
