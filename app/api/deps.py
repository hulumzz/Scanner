from fastapi import Header, Request
from app.core.security import require_admin, validate_csrf

def admin_required(request: Request): require_admin(request)
def csrf_required(request: Request, x_csrf_token: str | None = Header(default=None)):
    require_admin(request); validate_csrf(request, x_csrf_token)
