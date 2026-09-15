from app.schemas.extraction import HeaderExtraction, MergedMember
from app.services.validation_service import validate_extraction

def member(row,nik,status='Anak'): return MergedMember(no_urut_kk=row,nik=nik,nama_lengkap=f'ANGGOTA {row}',status_hubungan=status,tanggal_lahir='2000-01-01')
def test_invalid_kk_number(): assert 'INVALID_KK_NUMBER' in {x['code'] for x in validate_extraction(HeaderExtraction(no_kk='123'),[member(1,'3326000000000001','Kepala Keluarga')],[])}
def test_duplicate_nik_and_multiple_heads():
    codes={x['code'] for x in validate_extraction(HeaderExtraction(no_kk='3326000000000000'),[member(1,'3326000000000001','Kepala Keluarga'),member(2,'3326000000000001','Kepala Keluarga')],[])}; assert 'DUPLICATE_NIK' in codes; assert 'MULTIPLE_HEADS' in codes
