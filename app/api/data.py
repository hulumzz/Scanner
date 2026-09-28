from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import admin_required
from app.db.session import get_db
from app.models import KKRecord, ScanItem

router = APIRouter(prefix='/api/data', tags=['data'])


@router.get('', dependencies=[Depends(admin_required)])
def list_data(q: str | None = Query(default=None, max_length=100), status: str | None = None, offset: int = Query(default=0, ge=0), limit: int = Query(default=30, ge=1, le=100), db: Session = Depends(get_db)):
    conditions = [ScanItem.status == status] if status else []
    if q:
        conditions.append(or_(KKRecord.no_kk.contains(q), KKRecord.nama_kepala_keluarga.ilike(f'%{q}%')))
    item_stmt = select(ScanItem)
    count_stmt = select(func.count()).select_from(ScanItem)
    if q:
        item_stmt = item_stmt.join(ScanItem.kk_record)
        count_stmt = count_stmt.join(ScanItem.kk_record)
    items = db.scalars(item_stmt.where(*conditions).options(selectinload(ScanItem.kk_record).selectinload(KKRecord.members)).order_by(ScanItem.created_at.desc()).offset(offset).limit(limit)).all()
    total = db.scalar(count_stmt.where(*conditions)) or 0
    return {'items': [{'id': item.id, 'status': item.status, 'filename': item.original_filename, 'created_at': item.created_at, 'no_kk': item.kk_record.no_kk if item.kk_record else None, 'nama_kepala_keluarga': item.kk_record.nama_kepala_keluarga if item.kk_record else None, 'member_count': len(item.kk_record.members) if item.kk_record else 0} for item in items], 'total': total, 'offset': offset, 'limit': limit}
