import cv2
import numpy as np
from app.core.exceptions import ScannerError


def decode_image(data: bytes):
    arr = np.frombuffer(data, dtype=np.uint8); image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None: raise ScannerError('UNSUPPORTED_FORMAT', 'File gambar tidak dapat dibaca.')
    return image
