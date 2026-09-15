import json
from functools import lru_cache
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent

@lru_cache
def load_layout(name: str='kk_standard_v1')->dict: return json.loads((BASE/'layouts'/f'{name}.json').read_text(encoding='utf-8'))

def crop_region(image,region:dict):
    h,w=image.shape[:2]; x1=max(0,min(w-1,int(region['x1']*w))); y1=max(0,min(h-1,int(region['y1']*h))); x2=max(x1+1,min(w,int(region['x2']*w))); y2=max(y1+1,min(h,int(region['y2']*h))); return image[y1:y2,x1:x2]
