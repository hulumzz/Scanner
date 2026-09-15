from datetime import datetime
from app.schemas.extraction import MergedMember, PrimaryExtraction, SecondaryExtraction


def _parse_date(value):
    if not value or value.strip() in {'-',''}: return None
    for fmt in ('%Y-%m-%d','%d-%m-%Y','%d/%m/%Y','%d.%m.%Y'):
        try: return datetime.strptime(value.strip(),fmt).date()
        except ValueError: pass
    return None


def merge_rows(primary:PrimaryExtraction,secondary:SecondaryExtraction):
    pmap={r.row:r for r in primary.rows}; smap={r.row:r for r in secondary.rows}; members=[]; mismatches=[]
    for row in sorted(set(pmap)|set(smap)):
        p=pmap.get(row); s=smap.get(row)
        if p is None or s is None: mismatches.append(row)
        members.append(MergedMember(no_urut_kk=row,nik=p.nik if p else None,nama_lengkap=p.nama_lengkap if p else None,jenis_kelamin=p.jenis_kelamin if p else None,tempat_lahir=p.tempat_lahir if p else None,tanggal_lahir=_parse_date(p.tanggal_lahir) if p else None,agama=p.agama if p else None,pendidikan=p.pendidikan if p else None,jenis_pekerjaan=p.jenis_pekerjaan if p else None,status_perkawinan=p.status_perkawinan if p else None,golongan_darah=p.golongan_darah if p else None,status_hubungan=s.status_hubungan if s else None,kewarganegaraan=s.kewarganegaraan if s else None,no_paspor=s.no_paspor if s else None,no_kitas_kitap=s.no_kitas_kitap if s else None,nama_ayah=s.nama_ayah if s else None,nama_ibu=s.nama_ibu if s else None))
    return members,mismatches
