import cv2
from pydantic import ValidationError
from app.core.exceptions import ScannerError
from app.schemas.extraction import HeaderExtraction, PrimaryExtraction, SecondaryExtraction, ExtractionBundle
from app.services.layout_service import crop_region, load_layout
from app.services.row_mapper import merge_rows

POLICY='TRANSCRIBE ONLY. Do not infer. Do not guess unreadable characters. Return null if a value cannot be read reliably. Preserve row numbers exactly. Never move values between rows. Never derive family relationships yourself. Return ONLY valid JSON matching the requested structure.'
HEADER_PROMPT=POLICY+'\nRead only the KK header/household region. JSON keys: no_kk, nama_kepala_keluarga, alamat, rt, rw, kode_pos, dusun, desa, kecamatan, kabupaten, provinsi. Keep No KK as a string of visible digits. If unsure return null.'
PRIMARY_PROMPT=POLICY+'\nRead only the primary member table. Return {"rows":[...]}. Each row must include row plus visible values for nik, nama_lengkap, jenis_kelamin, tempat_lahir, tanggal_lahir, agama, pendidikan, jenis_pekerjaan, status_perkawinan, golongan_darah. Use YYYY-MM-DD for date only when confidently readable, otherwise null.'
SECONDARY_PROMPT=POLICY+'\nRead only the secondary member table. Return {"rows":[...]}. Each row must include row plus visible values for status_hubungan, kewarganegaraan, no_paspor, no_kitas_kitap, nama_ayah, nama_ibu. Preserve printed row number; never shift a missing row.'


def _encode_region(region):
    ok,buf=cv2.imencode('.jpg',region,[int(cv2.IMWRITE_JPEG_QUALITY),94])
    if not ok: raise ScannerError('AI_INVALID_RESPONSE','Gagal menyiapkan region gambar untuk AI.')
    return buf.tobytes()


async def extract_document(rectified,provider):
    layout=load_layout()
    try:
        hres=await provider.extract_json(_encode_region(crop_region(rectified,layout['header'])),'image/jpeg',HEADER_PROMPT)
        pres=await provider.extract_json(_encode_region(crop_region(rectified,layout['primary_table'])),'image/jpeg',PRIMARY_PROMPT)
        sres=await provider.extract_json(_encode_region(crop_region(rectified,layout['secondary_table'])),'image/jpeg',SECONDARY_PROMPT)
        header=HeaderExtraction.model_validate(hres.data); primary=PrimaryExtraction.model_validate(pres.data); secondary=SecondaryExtraction.model_validate(sres.data)
    except ValidationError as exc: raise ScannerError('AI_INVALID_RESPONSE','Struktur JSON AI tidak sesuai schema ekstraksi.',502) from exc
    members,mismatches=merge_rows(primary,secondary)
    return ExtractionBundle(header=header,primary=primary,secondary=secondary,members=members),mismatches,{'header':hres.metadata,'primary':pres.metadata,'secondary':sres.metadata}
