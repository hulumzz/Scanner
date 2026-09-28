from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import admin_required, csrf_required
from app.db.session import get_db
from app.models import Export, ExportItem, KKMember, KKRecord, ScanItem
from app.schemas.export import ExportCreate
from app.services.export_service import build_sid_workbook

router = APIRouter(prefix='/api/exports', tags=['exports'])


def utcnow():
    return datetime.now(timezone.utc)


def _items(db, ids):
    if not ids:
        return []
    return db.scalars(select(ScanItem).where(ScanItem.id.in_(ids), ScanItem.status == 'APPROVED').options(selectinload(ScanItem.kk_record).selectinload(KKRecord.members)).order_by(ScanItem.created_at)).all()


def _master_items(db):
    return db.scalars(select(ScanItem).where(ScanItem.status == 'APPROVED').options(selectinload(ScanItem.kk_record).selectinload(KKRecord.members)).order_by(ScanItem.created_at)).all()


@router.get('/master-summary', dependencies=[Depends(admin_required)])
def master_summary(db: Session = Depends(get_db)):
    kk_count = db.scalar(select(func.count()).select_from(ScanItem).where(ScanItem.status == 'APPROVED')) or 0
    row_count = db.scalar(select(func.count()).select_from(KKMember).join(KKRecord, KKMember.kk_record_id == KKRecord.id).join(ScanItem, KKRecord.scan_item_id == ScanItem.id).where(ScanItem.status == 'APPROVED')) or 0
    return {'kk_count': kk_count, 'row_count': row_count}


@router.get('/master/download', dependencies=[Depends(admin_required)])
def download_master(db: Session = Depends(get_db)):
    items = _master_items(db)
    if not items:
        raise HTTPException(422, 'Belum ada data APPROVED untuk diunduh.')
    data, rows = build_sid_workbook(items)
    filename = f'data-kependudukan-approved-{datetime.now():%Y%m%d}.xlsx'
    return Response(data, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={'Content-Disposition': f'attachment; filename="{filename}"', 'Cache-Control': 'no-store', 'X-Export-KK-Count': str(len(items)), 'X-Export-Row-Count': str(rows)})


@router.post('', dependencies=[Depends(csrf_required)])
def create_export(payload: ExportCreate, db: Session = Depends(get_db)):
    stmt = select(ScanItem.id).where(ScanItem.status == 'APPROVED')
    if payload.mode == 'unexported':
        stmt = stmt.where(ScanItem.exported_at.is_(None))
    elif payload.mode == 'selected':
        stmt = stmt.where(ScanItem.id.in_(payload.scan_item_ids))
    elif payload.mode == 'batch':
        stmt = stmt.where(ScanItem.batch_id == payload.batch_id)
    items = _items(db, list(db.scalars(stmt).all()))
    if not items:
        raise HTTPException(422, 'Tidak ada data APPROVED yang sesuai filter export.')
    _, rows = build_sid_workbook(items)
    now = datetime.now()
    count = db.query(Export).filter(Export.export_code.like(f'EXP-{now:%Y%m%d}-%')).count()
    code = f'EXP-{now:%Y%m%d}-{count + 1:04d}'
    export = Export(export_code=code, filter_description=payload.mode, row_count=rows, kk_count=len(items), filename=f'{code}-sid.xlsx')
    db.add(export)
    db.flush()
    for item in items:
        db.add(ExportItem(export_id=export.id, scan_item_id=item.id))
        item.exported_at = utcnow()
    db.commit()
    return {'id': export.id, 'export_code': code, 'filename': export.filename, 'row_count': rows, 'kk_count': len(items)}


@router.get('', dependencies=[Depends(admin_required)])
def list_exports(db: Session = Depends(get_db)):
    return [{'id': export.id, 'export_code': export.export_code, 'filter_description': export.filter_description, 'row_count': export.row_count, 'kk_count': export.kk_count, 'filename': export.filename, 'created_at': export.created_at} for export in db.scalars(select(Export).order_by(Export.created_at.desc()).limit(100)).all()]


@router.get('/{export_id}/download', dependencies=[Depends(admin_required)])
def download(export_id: str, db: Session = Depends(get_db)):
    export = db.scalar(select(Export).where(Export.id == export_id).options(selectinload(Export.items)))
    if not export:
        raise HTTPException(404, 'Export tidak ditemukan.')
    data, _ = build_sid_workbook(_items(db, [item.scan_item_id for item in export.items]))
    return Response(data, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={'Content-Disposition': f'attachment; filename="{export.filename}"', 'Cache-Control': 'no-store'})
