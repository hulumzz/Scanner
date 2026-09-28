"""Safely reset all KK Scanner operational data in the configured database.

Examples:
  py -3.12 scripts/reset_kk_data.py --dry-run
  py -3.12 scripts/reset_kk_data.py --confirm DELETE_ALL_KK_DATA
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

CONFIRMATION = 'DELETE_ALL_KK_DATA'


def print_counts(counts: dict[str, int]) -> None:
    for table, count in counts.items():
        print(f'  {table}: {count}')


def main() -> int:
    parser = argparse.ArgumentParser(description='Hapus seluruh data operasional KK Scanner.')
    parser.add_argument('--dry-run', action='store_true', help='Tampilkan jumlah data tanpa menghapus apa pun.')
    parser.add_argument('--confirm', help=f'Harus bernilai tepat {CONFIRMATION}.')
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        from app.db.session import SessionLocal
        from app.services.data_reset_service import operational_data_counts, reset_operational_data
    except Exception as exc:
        print('DATABASE_URL tidak dapat digunakan. Periksa konfigurasi koneksi Aiven tanpa mencetak kredensialnya.', file=sys.stderr)
        print(f'Penyebab: {exc.__class__.__name__}', file=sys.stderr)
        return 2

    with SessionLocal() as db:
        counts = operational_data_counts(db)
        print('Data yang akan dihapus:')
        print_counts(counts)
        if args.dry_run:
            print('Dry run selesai. Tidak ada data yang dihapus.')
            return 0
        if args.confirm != CONFIRMATION:
            print(f'Batal. Gunakan --confirm {CONFIRMATION} untuk menghapus data.', file=sys.stderr)
            return 2
        try:
            deleted = reset_operational_data(db)
        except Exception:
            db.rollback()
            raise
    print('Reset selesai. Data operasional yang dihapus:')
    print_counts(deleted)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
