from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse

from src.core.config import config
from .auth_helpers import verify_hashed_cookie


async def admin_auth(request: Request):
    admin_token = request.cookies.get("admin_token")
    user_role = request.cookies.get("user_role")
    
    if admin_token is None or user_role is None:
        return False
        
    if verify_hashed_cookie(admin_token, config.api.admin_login, config.api.secret_key):
        return user_role
    elif verify_hashed_cookie(admin_token, config.api.superuser_login, config.api.secret_key):
        return user_role
    else:
        return False


async def check_admin_auth(request: Request):
    admin_token = request.cookies.get("admin_token")
    if not admin_token or not verify_hashed_cookie(admin_token, config.api.admin_login, config.api.secret_key):
        return None 
    return True 

