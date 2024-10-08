from fastapi import HTTPException, Request

from src.core.config import settings
from .auth_helpers import verify_hashed_cookie



async def admin_auth(request: Request):
    admin_token = request.cookies.get("admin_token")
    if admin_token is None or not verify_hashed_cookie(admin_token, settings.api.admin_login, settings.api.seckret_key):
        raise HTTPException(status_code=302, detail="Redirecting to login", headers={"Location": "/auth/login"})
    return True

async def check_admin_auth(request: Request):
    admin_token = request.cookies.get("admin_token")
    if not admin_token or not verify_hashed_cookie(admin_token, settings.api.admin_login, settings.api.seckret_key):
        return None 
    return True 