import cv2
import numpy as np
from app.core.exceptions import ScannerError


def _order_points(pts):
    rect=np.zeros((4,2),dtype='float32'); s=pts.sum(axis=1); diff=np.diff(pts,axis=1).reshape(-1); rect[0]=pts[np.argmin(s)]; rect[2]=pts[np.argmax(s)]; rect[1]=pts[np.argmin(diff)]; rect[3]=pts[np.argmax(diff)]; return rect


def _four_point_transform(image, pts):
    rect=_order_points(pts); tl,tr,br,bl=rect; max_w=int(max(np.linalg.norm(br-bl),np.linalg.norm(tr-tl))); max_h=int(max(np.linalg.norm(tr-br),np.linalg.norm(tl-bl)))
    if max_w<600 or max_h<350: raise ScannerError('CROPPED_DOCUMENT','Area dokumen yang terdeteksi terlalu kecil atau terpotong.')
    dst=np.array([[0,0],[max_w-1,0],[max_w-1,max_h-1],[0,max_h-1]],dtype='float32'); return cv2.warpPerspective(image,cv2.getPerspectiveTransform(rect,dst),(max_w,max_h))


def rectify_document(image):
    h,w=image.shape[:2]; scale=1200/max(h,w) if max(h,w)>1200 else 1.0; small=cv2.resize(image,None,fx=scale,fy=scale) if scale!=1.0 else image.copy(); gray=cv2.GaussianBlur(cv2.cvtColor(small,cv2.COLOR_BGR2GRAY),(5,5),0); edges=cv2.dilate(cv2.Canny(gray,50,150),np.ones((3,3),np.uint8),iterations=1); contours,_=cv2.findContours(edges,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE); quad=None; area=small.shape[0]*small.shape[1]
    for contour in sorted(contours,key=cv2.contourArea,reverse=True)[:12]:
        approx=cv2.approxPolyDP(contour,0.02*cv2.arcLength(contour,True),True)
        if len(approx)==4 and cv2.contourArea(approx)>area*0.35: quad=approx.reshape(4,2).astype('float32'); break
    if quad is None:
        ratio=w/h if h else 0
        if 1.35<=ratio<=1.9: return image,{'rectified':False,'document_boundary':'assumed_full_frame'}
        raise ScannerError('PERSPECTIVE_FAILED','Empat sisi dokumen tidak dapat ditemukan dengan yakin.')
    rectified=_four_point_transform(image,quad/scale); rh,rw=rectified.shape[:2]; ratio=rw/rh if rh else 0
    if not 1.25<=ratio<=2.0: raise ScannerError('PERSPECTIVE_FAILED','Proporsi dokumen hasil koreksi tidak wajar.')
    return rectified,{'rectified':True,'document_boundary':'detected'}
