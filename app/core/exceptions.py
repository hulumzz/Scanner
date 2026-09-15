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
    'UNSUPPORTED_FORMAT': 'Format file tidak didukung. Gunakan JPG, PNG, atau WebP.',
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
