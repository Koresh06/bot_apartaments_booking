from typing import Annotated
from jose import jwt, JWTError
from fastapi import Depends, Security, Request
from fastapi.security import APIKeyCookie
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import config
from src.core.db_helper import get_db

from src.core.models import Users
from src.apmin_panel.api.auth.service import AuthApiRepo

from .jwt import ALGORITHM
from .schemas import TokenPayload


cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)


async def get_current_user(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    token: Annotated[
        str,
        Security(cookie_scheme),
    ]
):
    """Check auth user and redirect if inactive"""
    token = request.cookies.get("access_token")
    if not token: 
        return False
    try:
        payload = jwt.decode(token, config.api.secret_key, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except JWTError:
        False
        
    user: Users = await AuthApiRepo(session).get_user_by_id(user_id=token_data.user_id)
    if not user:
        False

    return user

