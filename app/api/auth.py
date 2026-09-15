from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from app.core.security import ensure_csrf_token, validate_csrf, verify_admin_credentials
router=APIRouter()

@router.get('/login')
def login_page(request:Request):
    if request.session.get('is_admin'): return RedirectResponse('/dashboard',303)
    return request.app.state.templates.TemplateResponse(request,'login.html',{'csrf_token':ensure_csrf_token(request),'error':None})

@router.post('/login')
def login(request:Request,username:str=Form(...),password:str=Form(...),csrf_token:str=Form(...)):
    validate_csrf(request,csrf_token)
    if not verify_admin_credentials(username,password):
        return request.app.state.templates.TemplateResponse(request,'login.html',{'csrf_token':ensure_csrf_token(request),'error':'Username atau password salah.'},status_code=401)
    request.session.clear(); request.session['is_admin']=True; ensure_csrf_token(request); return RedirectResponse('/dashboard',303)

@router.post('/logout')
def logout(request:Request,csrf_token:str=Form(...)):
    validate_csrf(request,csrf_token); request.session.clear(); return RedirectResponse('/login',303)
