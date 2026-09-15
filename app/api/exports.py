from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.api.deps import admin_required, csrf_required
from app.db.session import get_db
from app.models import Export, ExportItem, KKRecord, ScanItem
from app.schemas.export import ExportCreate
from app.services.export_service import build_sid_workbook
router=APIRouter(prefix='/api/exports',tags=['exports'])
def utcnow(): return datetime.now(timezone.utc)
def _items(db,ids): return db.scalars(select(ScanItem).where(ScanItem.id.in_(ids),ScanItem.status=='APPROVED').options(selectinload(ScanItem.kk_record).selectinload(KKRecord.members)).order_by(ScanItem.created_at)).all() if ids else []
@router.post('',dependencies=[Depends(csrf_required)])
def create_export(payload:ExportCreate,db:Session=Depends(get_db)):
    stmt=select(ScanItem.id).where(ScanItem.status=='APPROVED')
    if payload.mode=='unexported': stmt=stmt.where(ScanItem.exported_at.is_(None))
    elif payload.mode=='selected': stmt=stmt.where(ScanItem.id.in_(payload.scan_item_ids))
    elif payload.mode=='batch': stmt=stmt.where(ScanItem.batch_id==payload.batch_id)
    items=_items(db,list(db.scalars(stmt).all()))
    if not items: raise HTTPException(422,'Tidak ada data APPROVED yang sesuai filter export.')
    _,rows=build_sid_workbook(items); now=datetime.now(); n=db.query(Export).filter(Export.export_code.like(f'EXP-{now:%Y%m%d}-%')).count(); code=f'EXP-{now:%Y%m%d}-{n+1:04d}'; e=Export(export_code=code,filter_description=payload.mode,row_count=rows,kk_count=len(items),filename=f'{code}-sid.xlsx'); db.add(e); db.flush()
    for i in items: db.add(ExportItem(export_id=e.id,scan_item_id=i.id)); i.exported_at=utcnow()
    db.commit(); return {'id':e.id,'export_code':code,'filename':e.filename,'row_count':rows,'kk_count':len(items)}
@router.get('',dependencies=[Depends(admin_required)])
def list_exports(db:Session=Depends(get_db)):
    return [{'id':e.id,'export_code':e.export_code,'filter_description':e.filter_description,'row_count':e.row_count,'kk_count':e.kk_count,'filename':e.filename,'created_at':e.created_at} for e in db.scalars(select(Export).order_by(Export.created_at.desc()).limit(100)).all()]
@router.get('/{export_id}/download',dependencies=[Depends(admin_required)])
def download(export_id:str,db:Session=Depends(get_db)):
    e=db.scalar(select(Export).where(Export.id==export_id).options(selectinload(Export.items)))
    if not e: raise HTTPException(404,'Export tidak ditemukan.')
    data,_=build_sid_workbook(_items(db,[x.scan_item_id for x in e.items])); return Response(data,media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',headers={'Content-Disposition':f'attachment; filename="{e.filename}"','Cache-Control':'no-store'})
