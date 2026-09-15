from datetime import date
from pydantic import BaseModel


class KKUpdate(BaseModel):
    no_kk: str | None = None
    nama_kepala_keluarga: str | None = None
    alamat: str | None = None
    rt: str | None = None
    rw: str | None = None
    kode_pos: str | None = None
    dusun: str | None = None
    desa: str | None = None
    kecamatan: str | None = None
    kabupaten: str | None = None
    provinsi: str | None = None


class MemberUpdate(BaseModel):
    no_urut_kk: int | None = None
    status_hubungan: str | None = None
    nik: str | None = None
    nama_lengkap: str | None = None
    jenis_kelamin: str | None = None
    tempat_lahir: str | None = None
    tanggal_lahir: date | None = None
    agama: str | None = None
    pendidikan: str | None = None
    jenis_pekerjaan: str | None = None
    status_perkawinan: str | None = None
    kewarganegaraan: str | None = None
    no_paspor: str | None = None
    no_kitas_kitap: str | None = None
    nama_ayah: str | None = None
    nama_ibu: str | None = None
    golongan_darah: str | None = None
