from datetime import date
from pydantic import BaseModel, ConfigDict, Field, field_validator


class HeaderExtraction(BaseModel):
    model_config = ConfigDict(extra='ignore')
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


class PrimaryRow(BaseModel):
    model_config = ConfigDict(extra='ignore')
    row: int
    nik: str | None = None
    nama_lengkap: str | None = None
    jenis_kelamin: str | None = None
    tempat_lahir: str | None = None
    tanggal_lahir: str | None = None
    agama: str | None = None
    pendidikan: str | None = None
    jenis_pekerjaan: str | None = None
    status_perkawinan: str | None = None
    golongan_darah: str | None = None


class SecondaryRow(BaseModel):
    model_config = ConfigDict(extra='ignore')
    row: int
    status_hubungan: str | None = None
    kewarganegaraan: str | None = None
    no_paspor: str | None = None
    no_kitas_kitap: str | None = None
    nama_ayah: str | None = None
    nama_ibu: str | None = None


class PrimaryExtraction(BaseModel): rows: list[PrimaryRow] = Field(default_factory=list)
class SecondaryExtraction(BaseModel): rows: list[SecondaryRow] = Field(default_factory=list)


class MergedMember(BaseModel):
    no_urut_kk: int
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

    @field_validator('tanggal_lahir', mode='before')
    @classmethod
    def empty_date(cls, value): return None if value in ('', '-', None) else value


class ExtractionBundle(BaseModel):
    header: HeaderExtraction
    primary: PrimaryExtraction
    secondary: SecondaryExtraction
    members: list[MergedMember]
