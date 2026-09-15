import cv2
from app.core.config import get_settings


def make_thumbnail(image):
    settings=get_settings(); h,w=image.shape[:2]; scale=min(1.0,settings.thumbnail_long_edge/max(h,w)); thumb=cv2.resize(image,(max(1,int(w*scale)),max(1,int(h*scale))),interpolation=cv2.INTER_AREA); ok,buf=cv2.imencode('.webp',thumb,[int(cv2.IMWRITE_WEBP_QUALITY),60])
    if ok: return 'image/webp',buf.tobytes()
    ok,buf=cv2.imencode('.jpg',thumb,[int(cv2.IMWRITE_JPEG_QUALITY),65]); return 'image/jpeg',buf.tobytes()
