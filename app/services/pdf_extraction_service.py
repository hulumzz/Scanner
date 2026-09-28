"""Read selectable text from the one-page landscape KK print template.

The PDF remains in memory. Raster images, including the DRAFT watermark, are
not part of the text input and no AI provider is used.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from io import BytesIO

import fitz
from PIL import Image

from app.core.config import get_settings
from app.core.exceptions import ScannerError
from app.schemas.extraction import ExtractionBundle, HeaderExtraction, PrimaryExtraction, SecondaryExtraction
from app.services.row_mapper import merge_rows


# Cell boundaries are fractions of the landscape KK page width. The second
# table contains marital status; the first table does not.
_PRIMARY_COLUMNS = (
    ('row', 0.000, 0.030), ('nama_lengkap', 0.030, 0.240),
    ('nik', 0.240, 0.335), ('jenis_kelamin', 0.335, 0.385),
    ('tempat_lahir', 0.385, 0.505), ('tanggal_lahir', 0.505, 0.555),
    ('agama', 0.555, 0.615), ('pendidikan', 0.615, 0.760),
    ('jenis_pekerjaan', 0.760, 0.930), ('golongan_darah', 0.930, 1.001),
)
_SECONDARY_COLUMNS = (
    ('row', 0.000, 0.030), ('status_perkawinan', 0.030, 0.130),
    ('tanggal_perkawinan', 0.130, 0.190), ('status_hubungan', 0.190, 0.305),
    ('kewarganegaraan', 0.305, 0.400), ('no_paspor', 0.400, 0.477),
    ('no_kitas_kitap', 0.477, 0.555), ('nama_ayah', 0.555, 0.760),
    ('nama_ibu', 0.760, 1.001),
)


@dataclass(frozen=True)
class PdfWord:
    x0: float
    y0: float
    x1: float
    y1: float
    text: str

    @property
    def x_center(self) -> float:
        return (self.x0 + self.x1) / 2

    @property
    def y_center(self) -> float:
        return (self.y0 + self.y1) / 2


@dataclass
class NativePdfResult:
    bundle: ExtractionBundle
    thumbnail_mime: str
    thumbnail_data: bytes
    metadata: dict


def _normalise_value(value: str) -> str | None:
    value = re.sub(r'\s+', ' ', value).strip(' \t:|-')
    return value or None


def _words(page: fitz.Page) -> list[PdfWord]:
    return [
        PdfWord(x0, y0, x1, y1, text.strip())
        for x0, y0, x1, y1, text, *_ in page.get_text('words', sort=True)
        if text.strip() and text.strip().upper() != 'DRAFT'
    ]


def _cell(words: list[PdfWord], width: float, left: float, right: float) -> str | None:
    selected = [word for word in words if left <= word.x_center / width < right]
    return _normalise_value(' '.join(word.text for word in sorted(selected, key=lambda word: word.x0)))


def _header(words: list[PdfWord], width: float, height: float) -> HeaderExtraction:
    top_numbers = {
        word.text for word in words
        if word.y_center < height * 0.105 and 0.2 < word.x_center / width < 0.8
        and re.fullmatch(r'\d{16}', word.text)
    }
    values: dict[str, str | None] = {'no_kk': next(iter(top_numbers)) if len(top_numbers) == 1 else None}
    label_map = {
        'NAMA KEPALA KELUARGA': 'nama_kepala_keluarga',
        'ALAMAT': 'alamat', 'RT / RW': 'rt_rw', 'KODE POS': 'kode_pos',
        'DESA / KELURAHAN': 'desa', 'KECAMATAN': 'kecamatan',
        'KABUPATEN / KOTA': 'kabupaten', 'PROVINSI': 'provinsi',
    }
    header_words = [word for word in words if 0.10 <= word.y_center / height <= 0.175]
    for label, key in label_map.items():
        label_parts = label.replace(' / ', ' ').split()
        label_zone = (0.13, 0.265) if key in {'nama_kepala_keluarga', 'alamat', 'rt_rw', 'kode_pos'} else (0.58, 0.685)
        value_zone = (0.265, 0.58) if label_zone[0] == 0.13 else (0.685, 0.93)
        candidates = [word for word in header_words if label_zone[0] <= word.x_center / width < label_zone[1]]
        anchor = next((word for word in candidates if (word.text.upper().replace('/', ' ').strip(': ').split() or [''])[0] == label_parts[0]), None)
        if anchor is None:
            continue
        row_words = [word for word in header_words if abs(word.y_center - anchor.y_center) <= 2.5]
        row_label = _cell(row_words, width, *label_zone) or ''
        if not all(part in row_label.upper().replace('/', ' ').split() for part in label_parts):
            continue
        value = _cell(row_words, width, *value_zone)
        if key == 'rt_rw':
            numbers = re.findall(r'\d{1,3}', value or '')
            if len(numbers) == 2:
                values['rt'], values['rw'] = numbers
        elif key == 'kode_pos':
            match = re.search(r'\b\d{5}\b', value or '')
            values[key] = match.group() if match else None
        else:
            values[key] = value
    if not values['no_kk'] or not values.get('nama_kepala_keluarga'):
        raise ScannerError('PDF_TABLE_UNREADABLE', 'Header KK tidak cocok dengan blanko yang didukung.')
    return HeaderExtraction(**values)


def _table_rows(words: list[PdfWord], width: float, height: float, y1: float, y2: float, columns: tuple, primary: bool) -> list[dict]:
    region = [word for word in words if y1 <= word.y_center / height <= y2]
    markers = [word for word in region if word.x_center / width < 0.03 and re.fullmatch(r'(?:[1-9]|10)', word.text)]
    rows: list[dict] = []
    for marker in sorted(markers, key=lambda word: word.y_center):
        line = [word for word in region if abs(word.y_center - marker.y_center) <= 4.0]
        values = {name: _cell(line, width, left, right) for name, left, right in columns}
        if values['row'] != marker.text:
            raise ScannerError('PDF_TABLE_UNREADABLE', 'Nomor baris tabel tidak konsisten.')
        values['row'] = int(marker.text)
        if primary:
            # Empty printable slots carry a row number and hyphens, but are not people.
            if not values['nama_lengkap'] and not values['nik']:
                continue
        elif not any(value for key, value in values.items() if key not in {'row', 'tanggal_perkawinan'}):
            continue
        values.pop('tanggal_perkawinan', None)
        rows.append(values)
    row_numbers = [row['row'] for row in rows]
    if len(row_numbers) != len(set(row_numbers)):
        raise ScannerError('PDF_TABLE_UNREADABLE', 'Nomor baris tabel terduplikasi.')
    return rows


def _matches_landscape_template(words: list[PdfWord], width: float, height: float) -> bool:
    primary_heading = any(
        word.text.upper() == 'NIK' and 0.26 <= word.x_center / width <= 0.34
        and 0.17 <= word.y_center / height <= 0.22 for word in words
    )
    secondary_heading = any(
        word.text.upper() == 'KEWARGANEGARAAN' and 0.30 <= word.x_center / width <= 0.41
        and 0.43 <= word.y_center / height <= 0.49 for word in words
    )
    return primary_heading and secondary_heading


def _thumbnail(page: fitz.Page) -> tuple[str, bytes]:
    scale = min(1.5, 900 / max(page.rect.width, page.rect.height))
    pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    image = Image.open(BytesIO(pixmap.tobytes('png')))
    image.thumbnail((get_settings().thumbnail_long_edge, get_settings().thumbnail_long_edge))
    output = BytesIO()
    image.save(output, format='WEBP', quality=60, method=4)
    return 'image/webp', output.getvalue()


def extract_pdf_document(data: bytes) -> NativePdfResult:
    settings = get_settings()
    try:
        document = fitz.open(stream=data, filetype='pdf')
    except (fitz.FileDataError, RuntimeError, ValueError) as exc:
        raise ScannerError('PDF_INVALID', 'File PDF tidak dapat dibuka.') from exc
    try:
        if document.needs_pass:
            raise ScannerError('PDF_ENCRYPTED', 'PDF terkunci sandi.')
        if document.page_count > settings.max_pdf_pages:
            raise ScannerError('PDF_TOO_MANY_PAGES', 'Jumlah halaman PDF melebihi batas.')
        if document.page_count != 1:
            raise ScannerError('PDF_INVALID', 'PDF tidak memiliki halaman.')
        page = document[0]
        words = _words(page)
        if sum(len(word.text) for word in words) < settings.min_pdf_text_characters:
            raise ScannerError('PDF_NO_SELECTABLE_TEXT', 'PDF tidak memiliki cukup teks native.')
        width, height = page.rect.width, page.rect.height
        if not 1.25 <= width / height <= 1.6:
            raise ScannerError('PDF_TABLE_UNREADABLE', 'Ukuran halaman tidak cocok dengan blanko KK.')
        if not _matches_landscape_template(words, width, height):
            raise ScannerError('PDF_TABLE_UNREADABLE', 'Susunan kolom tidak cocok dengan blanko KK.')
        header = _header(words, width, height)
        primary = PrimaryExtraction(rows=_table_rows(words, width, height, 0.24, 0.43, _PRIMARY_COLUMNS, True))
        secondary = SecondaryExtraction(rows=_table_rows(words, width, height, 0.50, 0.70, _SECONDARY_COLUMNS, False))
        if not primary.rows or {row.row for row in primary.rows} != {row.row for row in secondary.rows}:
            raise ScannerError('PDF_TABLE_UNREADABLE', 'Baris anggota pada kedua tabel tidak cocok.')
        members, mismatches = merge_rows(primary, secondary)
        bundle = ExtractionBundle(header=header, primary=primary, secondary=secondary, members=members)
        thumbnail_mime, thumbnail_data = _thumbnail(page)
        return NativePdfResult(
            bundle=bundle, thumbnail_mime=thumbnail_mime, thumbnail_data=thumbnail_data,
            metadata={'source_type': 'native_pdf_text', 'parser': 'kk-landscape-v2', 'page_count': 1, 'word_count': len(words), 'row_mismatches': mismatches},
        )
    finally:
        document.close()
