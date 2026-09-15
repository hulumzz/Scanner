from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload
from app.api.deps import admin_required
from app.db.session import get_db
from app.models import KKRecord, ScanItem
router=APIRouter(prefix='/api/data',tags=['data'])
@router.get('',dependencies=[Depends(admin_required)])
def list_data(q:str|None=Query(default=None,max_length=100),status:str|None=None,db:Session=Depends(get_db)):
    stmt=select(ScanItem).options(selectinload(ScanItem.kk_record).selectinload(KKRecord.members)).order_by(ScanItem.created_at.desc())
    if status: stmt=stmt.where(ScanItem.status==status)
    if q: stmt=stmt.join(ScanItem.kk_record).where(or_(KKRecord.no_kk.contains(q),KKRecord.nama_kepala_keluarga.ilike(f'%{q}%')))
    items=db.scalars(stmt.limit(200)).all(); return [{'id':i.id,'status':i.status,'filename':i.original_filename,'created_at':i.created_at,'no_kk':i.kk_record.no_kk if i.kk_record else None,'nama_kepala_keluarga':i.kk_record.nama_kepala_keluarga if i.kk_record else None,'member_count':len(i.kk_record.members) if i.kk_record else 0,'exported_at':i.exported_at} for i in items]
