import time
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload
from app.api.deps import admin_required, csrf_required
from app.core.config import get_settings
from app.core.exceptions import ERROR_MESSAGES, ScannerError
from app.core.logging import safe_scan_log
from app.core.security import hash_file
from app.db.session import get_db
from app.models import FieldCorrection, KKMember, KKRecord, ScanAttempt, ScanIssue, ScanItem
from app.providers import get_vision_provider
from app.schemas.extraction import HeaderExtraction, MergedMember
from app.schemas.kk import KKUpdate, MemberUpdate
from app.services.document_detector import rectify_document
from app.services.extraction_service import extract_document
from app.services.image_optimizer import decode_image
from app.services.quality_checker import inspect_quality
from app.services.thumbnail_service import make_thumbnail
from app.services.validation_service import validate_extraction
from app.services.verification_service import verify_critical_fields
router=APIRouter(prefix='/api',tags=['scans'])
def utcnow(): return datetime.now(timezone.utc)
def _detect_mime(data):
    if data.startswith(b'\xff\xd8\xff'): return 'image/jpeg'
    if data.startswith(b'\x89PNG\r\n\x1a\n'): return 'image/png'
    if len(data)>=12 and data[:4]==b'RIFF' and data[8:12]==b'WEBP': return 'image/webp'
    return None

def _load(db,id): return db.scalar(select(ScanItem).where(ScanItem.id==id).options(selectinload(ScanItem.kk_record).selectinload(KKRecord.members),selectinload(ScanItem.issues),selectinload(ScanItem.attempts)))
def _serialize(i):
    r=i.kk_record
    return {'id':i.id,'batch_id':i.batch_id,'item_number':i.item_number,'original_filename':i.original_filename,'status':i.status,'failure_code':i.failure_code,'failure_message':i.failure_message,'quality_metrics':i.quality_metrics,'approved_at':i.approved_at,'exported_at':i.exported_at,'kk':None if not r else {k:getattr(r,k) for k in ['id','no_kk','nama_kepala_keluarga','alamat','rt','rw','kode_pos','dusun','desa','kecamatan','kabupaten','provinsi']},'members':[] if not r else [{k:getattr(m,k) for k in ['id','no_urut_kk','status_hubungan','nik','nama_lengkap','jenis_kelamin','tempat_lahir','tanggal_lahir','agama','pendidikan','jenis_pekerjaan','status_perkawinan','kewarganegaraan','no_paspor','no_kitas_kitap','nama_ayah','nama_ibu','golongan_darah']} for m in r.members],'issues':[{'id':x.id,'severity':x.severity,'code':x.code,'field_name':x.field_name,'message':x.message,'resolved':x.resolved} for x in i.issues]}

def _save(db,item,bundle,issues):
    db.execute(delete(ScanIssue).where(ScanIssue.scan_item_id==item.id))
    if item.kk_record: db.delete(item.kk_record); db.flush()
    h=bundle.header; r=KKRecord(scan_item_id=item.id,no_kk=h.no_kk,nama_kepala_keluarga=h.nama_kepala_keluarga,alamat=h.alamat,rt=h.rt,rw=h.rw,kode_pos=h.kode_pos,dusun=h.dusun,desa=h.desa,kecamatan=h.kecamatan,kabupaten=h.kabupaten,provinsi=h.provinsi); db.add(r); db.flush(); rowmap={}
    for m in bundle.members:
        x=KKMember(kk_record_id=r.id,**m.model_dump()); db.add(x); db.flush(); rowmap[m.no_urut_kk]=x.id
    for issue in issues: db.add(ScanIssue(scan_item_id=item.id,member_id=rowmap.get(issue.get('row')),severity=issue['severity'],code=issue['code'],field_name=issue.get('field_name'),message=issue['message']))

async def _process(item_id,file,db):
    settings=get_settings(); item=_load(db,item_id)
    if not item: raise HTTPException(404,'Scan item tidak ditemukan.')
    data=await file.read(settings.max_upload_bytes+1)
    if len(data)>settings.max_upload_bytes: raise HTTPException(413,ERROR_MESSAGES['FILE_TOO_LARGE'])
    if not _detect_mime(data): raise HTTPException(415,ERROR_MESSAGES['UNSUPPORTED_FORMAT'])
    attempt=ScanAttempt(scan_item_id=item.id,attempt_number=len(item.attempts)+1,provider=settings.vision_provider,model=settings.vision_model,status='PROCESSING'); db.add(attempt); db.flush(); item.current_attempt_id=attempt.id; item.status='PROCESSING'; item.file_hash=hash_file(data); item.optimized_size=len(data); db.commit(); started=time.perf_counter()
    try:
        image=decode_image(data); h,w=image.shape[:2]; item.image_width=w; item.image_height=h; metrics=inspect_quality(image); rectified,det=rectify_document(image); metrics.update(det); item.quality_metrics=metrics; item.thumbnail_mime,item.thumbnail_data=make_thumbnail(rectified); provider=get_vision_provider(); bundle,mismatches,meta=await extract_document(rectified,provider); issues=validate_extraction(bundle.header,bundle.members,mismatches); verification=await verify_critical_fields(rectified,provider,issues)
        if verification: meta['verification']=verification; issues.append({'code':'VERIFICATION_PERFORMED','message':'Pembacaan verifikasi dijalankan. Periksa hasil sebelum approval.','field_name':None,'severity':'WARNING','row':None})
        _save(db,item,bundle,issues); item.status='REVIEW_REQUIRED' if issues else 'EXTRACTED'; attempt.status='SUCCESS'; attempt.extraction_snapshot=bundle.model_dump(mode='json'); attempt.provider_metadata=meta; attempt.completed_at=utcnow(); attempt.processing_ms=int((time.perf_counter()-started)*1000); db.commit(); safe_scan_log(scan_id=item.id,status=item.status,provider=settings.vision_provider,model=settings.vision_model,member_count=len(bundle.members),issue_count=len(issues),processing_ms=attempt.processing_ms); return _serialize(_load(db,item.id))
    except ScannerError as exc:
        db.rollback(); item=_load(db,item_id); attempt=db.get(ScanAttempt,attempt.id); item.status='FAILED'; item.failure_code=exc.code; item.failure_message=ERROR_MESSAGES.get(exc.code,exc.message); attempt.status='FAILED'; attempt.failure_code=exc.code; attempt.completed_at=utcnow(); attempt.processing_ms=int((time.perf_counter()-started)*1000); db.commit(); return _serialize(_load(db,item.id))

@router.post('/scan-items/{item_id}/process',dependencies=[Depends(csrf_required)])
async def process_item(item_id:str,file:UploadFile=File(...),db:Session=Depends(get_db)): return await _process(item_id,file,db)
@router.post('/scan-items/{item_id}/retry',dependencies=[Depends(csrf_required)])
async def retry_item(item_id:str,file:UploadFile=File(...),db:Session=Depends(get_db)): return await _process(item_id,file,db)
@router.get('/scan-items/{item_id}',dependencies=[Depends(admin_required)])
def get_item(item_id:str,db:Session=Depends(get_db)):
    i=_load(db,item_id)
    if not i: raise HTTPException(404,'Scan item tidak ditemukan.')
    return _serialize(i)
@router.get('/scan-items/{item_id}/thumbnail',dependencies=[Depends(admin_required)])
def thumbnail(item_id:str,db:Session=Depends(get_db)):
    i=db.get(ScanItem,item_id)
    if not i or not i.thumbnail_data: raise HTTPException(404,'Thumbnail tidak tersedia.')
    return Response(i.thumbnail_data,media_type=i.thumbnail_mime or 'image/webp')

def _corr(db,item_id,member_id,field,old,new):
    if str(old or '')!=str(new or ''): db.add(FieldCorrection(scan_item_id=item_id,member_id=member_id,field_name=field,original_value=None if old is None else str(old),corrected_value=None if new is None else str(new)))
@router.patch('/scan-items/{item_id}/kk',dependencies=[Depends(csrf_required)])
def update_kk(item_id:str,payload:KKUpdate,db:Session=Depends(get_db)):
    i=_load(db,item_id)
    if not i or not i.kk_record: raise HTTPException(404,'Data KK tidak ditemukan.')
    for f,v in payload.model_dump(exclude_unset=True).items(): _corr(db,i.id,None,f,getattr(i.kk_record,f),v); setattr(i.kk_record,f,v)
    i.status='REVIEW_REQUIRED'; i.approved_at=None; db.commit(); return _serialize(_load(db,i.id))
@router.patch('/members/{member_id}',dependencies=[Depends(csrf_required)])
def update_member(member_id:str,payload:MemberUpdate,db:Session=Depends(get_db)):
    m=db.get(KKMember,member_id)
    if not m: raise HTTPException(404,'Anggota tidak ditemukan.')
    r=db.get(KKRecord,m.kk_record_id); i=db.get(ScanItem,r.scan_item_id)
    for f,v in payload.model_dump(exclude_unset=True).items(): _corr(db,i.id,m.id,f,getattr(m,f),v); setattr(m,f,v)
    i.status='REVIEW_REQUIRED'; i.approved_at=None; db.commit(); return {'ok':True}
@router.post('/scan-items/{item_id}/approve',dependencies=[Depends(csrf_required)])
def approve(item_id:str,db:Session=Depends(get_db)):
    i=_load(db,item_id)
    if not i or not i.kk_record: raise HTTPException(404,'Data KK tidak ditemukan.')
    r=i.kk_record; h=HeaderExtraction(**{k:getattr(r,k) for k in ['no_kk','nama_kepala_keluarga','alamat','rt','rw','kode_pos','dusun','desa','kecamatan','kabupaten','provinsi']}); members=[MergedMember(**{k:getattr(m,k) for k in ['no_urut_kk','status_hubungan','nik','nama_lengkap','jenis_kelamin','tempat_lahir','tanggal_lahir','agama','pendidikan','jenis_pekerjaan','status_perkawinan','kewarganegaraan','no_paspor','no_kitas_kitap','nama_ayah','nama_ibu','golongan_darah']}) for m in r.members]; issues=validate_extraction(h,members,[]); blocking=[x for x in issues if x['severity'] in {'ERROR','CRITICAL'}]
    if blocking: raise HTTPException(422,{'message':'Data masih memiliki masalah yang harus diperbaiki.','issues':blocking})
    i.status='APPROVED'; i.approved_at=utcnow(); db.commit(); return _serialize(_load(db,i.id))
