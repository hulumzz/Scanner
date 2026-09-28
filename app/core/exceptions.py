from dataclasses import dataclass


@dataclass
class ScannerError(Exception):
    code: str
    message: str
    http_status: int = 422

    def __str__(self) -> str:
        return self.message


ERROR_MESSAGES = {
    'FILE_TOO_LARGE': 'Ukuran file terlalu besar.',
    'UNSUPPORTED_FORMAT': 'Format file tidak didukung. Gunakan PDF, JPG, PNG, atau WebP.',
    'PDF_TOO_LARGE': 'Ukuran PDF terlalu besar.',
    'PDF_INVALID': 'File PDF tidak valid atau rusak.',
    'PDF_ENCRYPTED': 'PDF terkunci sandi dan tidak dapat diproses.',
    'PDF_TOO_MANY_PAGES': 'PDF KK harus terdiri dari satu halaman.',
    'PDF_NO_SELECTABLE_TEXT': 'PDF ini tidak memiliki teks yang dapat dipilih. Unggah PDF KK dengan teks selectable.',
    'PDF_TABLE_UNREADABLE': 'Struktur tabel pada PDF tidak dapat dipetakan dengan aman. Periksa PDF atau lakukan entri manual.',
    'DUPLICATE_DOCUMENT': 'Dokumen ini sudah pernah diunggah.',
    'DUPLICATE_HOUSEHOLD': 'Nomor KK ini sudah ada pada hasil scan.',
    'PROCESSING_FAILED': 'Pemrosesan dokumen gagal secara tak terduga. Silakan coba lagi.',
    'VISION_FALLBACK_DISABLED': 'Pemrosesan foto dengan AI belum diaktifkan. Gunakan PDF KK dengan teks selectable.',
    'LOW_RESOLUTION': 'Resolusi foto terlalu rendah untuk dibaca dengan aman.',
    'BLUR': 'Foto terlalu buram. Ambil ulang foto dengan kamera stabil.',
    'DARK': 'Foto terlalu gelap. Ambil ulang di tempat yang lebih terang.',
    'GLARE': 'Pantulan cahaya terlalu kuat pada dokumen.',
    'CROPPED_DOCUMENT': 'Sebagian sisi Kartu Keluarga tidak terlihat.',
    'PERSPECTIVE_FAILED': 'Sudut foto terlalu ekstrem dan dokumen tidak dapat diluruskan.',
    'NOT_KK': 'Dokumen tidak dapat dikenali sebagai Kartu Keluarga.',
    'AI_TIMEOUT': 'Layanan pembaca dokumen melewati batas waktu.',
    'AI_RATE_LIMIT': 'Layanan pembaca dokumen sedang membatasi permintaan. Coba lagi nanti.',
    'AI_INVALID_RESPONSE': 'Respons pembaca dokumen tidak memiliki struktur yang valid.',
}
