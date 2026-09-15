from collections import Counter
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload
from app.api.deps import admin_required, csrf_required
from app.core.config import get_settings
from app.db.session import get_db
from app.models import ScanBatch, ScanItem
from app.schemas.batch import BatchCreate, ScanItemCreate
router=APIRouter(prefix='/api/batches',tags=['batches'])

def serialize_batch(batch):
    c=Counter(i.status for i in batch.items)
    return {'id':batch.id,'batch_code':batch.batch_code,'status':batch.status,'created_at':batch.created_at,'total':len(batch.items),'queued':c['QUEUED'],'processing':c['PROCESSING'],'extracted':c['EXTRACTED'],'review_required':c['REVIEW_REQUIRED'],'approved':c['APPROVED'],'failed':c['FAILED'],'items':[{'id':i.id,'item_number':i.item_number,'original_filename':i.original_filename,'status':i.status,'failure_code':i.failure_code,'failure_message':i.failure_message} for i in sorted(batch.items,key=lambda x:x.item_number)]}

@router.post('',dependencies=[Depends(csrf_required)])
def create_batch(payload:BatchCreate,db:Session=Depends(get_db)):
    if len(payload.filenames)>get_settings().max_batch_items: raise HTTPException(422,'Maksimal 20 foto per batch.')
    today=datetime.now().strftime('%Y%m%d'); existing=db.scalar(select(func.count()).select_from(ScanBatch).where(ScanBatch.batch_code.like(f'SCAN-{today}-%'))) or 0; batch=ScanBatch(batch_code=f'SCAN-{today}-{existing+1:04d}',status='QUEUED'); db.add(batch); db.flush()
    for idx,filename in enumerate(payload.filenames,1): db.add(ScanItem(batch_id=batch.id,item_number=idx,original_filename=filename,status='QUEUED'))
    db.commit(); batch=db.scalar(select(ScanBatch).where(ScanBatch.id==batch.id).options(selectinload(ScanBatch.items))); return serialize_batch(batch)

@router.get('',dependencies=[Depends(admin_required)])
def list_batches(db:Session=Depends(get_db)):
    return [serialize_batch(b) for b in db.scalars(select(ScanBatch).options(selectinload(ScanBatch.items)).order_by(ScanBatch.created_at.desc()).limit(100)).all()]

@router.get('/{batch_id}',dependencies=[Depends(admin_required)])
def get_batch(batch_id:str,db:Session=Depends(get_db)):
    b=db.scalar(select(ScanBatch).where(ScanBatch.id==batch_id).options(selectinload(ScanBatch.items)))
    if not b: raise HTTPException(404,'Batch tidak ditemukan.')
    return serialize_batch(b)
