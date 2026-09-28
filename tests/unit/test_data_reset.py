from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models import Export, ExportItem, FieldCorrection, KKMember, KKRecord, ScanAttempt, ScanBatch, ScanIssue, ScanItem
from app.services.data_reset_service import operational_data_counts, reset_operational_data


def test_reset_operational_data_removes_all_scanner_records():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    session = Session(engine)
    try:
        batch = ScanBatch(batch_code='TEST-RESET', status='QUEUED')
        item = ScanItem(batch=batch, item_number=1, original_filename='fictitious.pdf', status='APPROVED')
        record = KKRecord(scan_item=item, no_kk='0012345678901234', alamat='DK BOJONGIRENG')
        member = KKMember(kk_record=record, no_urut_kk=1, nik='0012345678901235')
        session.add(batch)
        session.flush()
        session.add_all([
            ScanAttempt(scan_item=item, attempt_number=1, provider='test', model='test'),
            ScanIssue(scan_item=item, member_id=member.id, severity='WARNING', code='TEST', message='Fiktif'),
            FieldCorrection(scan_item_id=item.id, member_id=member.id, field_name='alamat'),
        ])
        session.add(ExportItem(export=Export(export_code='EXP-TEST', filename='test.xlsx'), scan_item_id=item.id))
        session.commit()

        before = operational_data_counts(session)
        assert all(count == 1 for count in before.values())
        assert reset_operational_data(session) == before
        assert operational_data_counts(session) == {table: 0 for table in before}
    finally:
        session.close()
