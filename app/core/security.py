import hashlib
import hmac
import secrets
from fastapi import HTTPException, Request, status
from app.core.config import get_settings


def verify_admin_credentials(username: str, password: str) -> bool:
    settings = get_settings()
    return hmac.compare_digest(username, settings.admin_username) and hmac.compare_digest(password, settings.admin_password)


def ensure_csrf_token(request: Request) -> str:
    token = request.session.get('csrf_token')
    if not token:
        token = secrets.token_urlsafe(32)
        request.session['csrf_token'] = token
    return token


def validate_csrf(request: Request, supplied: str | None) -> None:
    expected = request.session.get('csrf_token')
    if not expected or not supplied or not hmac.compare_digest(expected, supplied):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='CSRF token tidak valid.')


def require_admin(request: Request) -> None:
    if not request.session.get('is_admin'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Autentikasi diperlukan.')


def hash_file(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
