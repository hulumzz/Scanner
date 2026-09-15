from app.schemas.extraction import PrimaryExtraction, SecondaryExtraction
from app.services.row_mapper import merge_rows

def test_missing_secondary_row_does_not_shift():
    primary=PrimaryExtraction(rows=[{'row':1,'nik':'3326000000000001','nama_lengkap':'A'},{'row':2,'nik':'3326000000000002','nama_lengkap':'B'},{'row':3,'nik':'3326000000000003','nama_lengkap':'C'}]); secondary=SecondaryExtraction(rows=[{'row':1,'nama_ayah':'AYAH A'},{'row':3,'nama_ayah':'AYAH C'}]); members,mismatches=merge_rows(primary,secondary); assert mismatches==[2]; assert members[1].no_urut_kk==2; assert members[1].nama_ayah is None; assert members[2].nama_ayah=='AYAH C'
