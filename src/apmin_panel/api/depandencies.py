from fastapi import HTTPException, Request

from src.core.config import config
from .auth_helpers import verify_hashed_cookie


async def admin_auth(request: Request):
    admin_token = request.cookies.get("admin_token")
    if admin_token is None or not verify_hashed_cookie(admin_token, config.api.admin_login, config.api.secret_key):
        raise HTTPException(status_code=302, detail="Redirecting to login", headers={"Location": "/auth/login"})
    return True


async def check_admin_auth(request: Request):
    admin_token = request.cookies.get("admin_token")
    if not admin_token or not verify_hashed_cookie(admin_token, config.api.admin_login, config.api.secret_key):
        return None 
    return True 