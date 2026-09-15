import cv2
import numpy as np
from app.core.config import get_settings
from app.core.exceptions import ScannerError


def inspect_quality(image) -> dict:
    settings = get_settings(); height, width = image.shape[:2]; gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var()); brightness = float(gray.mean()); contrast = float(gray.std()); glare_ratio = float(np.mean(gray > 248))
    metrics = {'width': width, 'height': height, 'blur_score': round(blur_score,2), 'brightness': round(brightness,2), 'contrast': round(contrast,2), 'glare_ratio': round(glare_ratio,4)}
    if max(width,height) < settings.min_effective_width: raise ScannerError('LOW_RESOLUTION','Resolusi gambar terlalu rendah untuk ekstraksi aman.')
    if blur_score < 45: raise ScannerError('BLUR','Foto terlalu buram untuk dibaca dengan aman.')
    if brightness < 45 or contrast < 18: raise ScannerError('DARK','Foto terlalu gelap atau kontras terlalu rendah.')
    if glare_ratio > 0.14: raise ScannerError('GLARE','Pantulan cahaya menutupi terlalu banyak area dokumen.')
    return metrics
