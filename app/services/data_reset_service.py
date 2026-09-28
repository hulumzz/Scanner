"""Controlled deletion of KK Scanner operational data."""
from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models import Export, ExportItem, FieldCorrection, KKMember, KKRecord, ScanAttempt, ScanBatch, ScanIssue, ScanItem


# Child tables must be removed before their referenced records so this works on
# Aiven PostgreSQL and local SQLite alike, without relying on FK cascade setup.
OPERATIONAL_MODELS = (
    ExportItem,
    FieldCorrection,
    ScanIssue,
    ScanAttempt,
    KKMember,
    KKRecord,
    Export,
    ScanItem,
    ScanBatch,
)


def operational_data_counts(db: Session) -> dict[str, int]:
    return {model.__tablename__: db.scalar(select(func.count()).select_from(model)) or 0 for model in OPERATIONAL_MODELS}


def reset_operational_data(db: Session) -> dict[str, int]:
    """Delete scanner data only; credentials and database schema remain intact."""
    counts = operational_data_counts(db)
    for model in OPERATIONAL_MODELS:
        db.execute(delete(model))
    db.commit()
    return counts
