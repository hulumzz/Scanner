import cv2
from app.services.layout_service import crop_region, load_layout
VERIFY_POLICY='TRANSCRIBE ONLY. This is a verification pass. Read only the requested values from the image. Do not infer, correct, or choose between candidates. Return JSON with a `values` object. Return null when unreadable.'


async def verify_critical_fields(rectified,provider,issues):
    targets=[{'field':i.get('field_name'),'row':i.get('row')} for i in issues if i['code'] in {'INVALID_KK_NUMBER','INVALID_NIK','UNREADABLE_FIELD'}]
    if not targets: return {}
    layout=load_layout(); region_name='header' if all(t['field']=='no_kk' for t in targets) else 'primary_table'; region=crop_region(rectified,layout[region_name]); ok,buf=cv2.imencode('.jpg',region,[int(cv2.IMWRITE_JPEG_QUALITY),95])
    if not ok: return {}
    result=await provider.extract_json(buf.tobytes(),'image/jpeg',VERIFY_POLICY+'\nRequested targets: '+str(targets)); return result.data
