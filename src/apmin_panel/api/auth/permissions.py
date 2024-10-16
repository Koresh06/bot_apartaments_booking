from typing import Annotated
from fastapi.responses import RedirectResponse
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, Security, Request
from fastapi.security import APIKeyCookie
from starlette.status import HTTP_403_FORBIDDEN
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
    except JWTError as e:
        False
        
    user: Users = await AuthApiRepo(session).get_user_by_id(user_id=token_data.user_id)
    if not user:
        False

    return user


# def get_admin(current_user: Users = Security(get_current_user)):
#     """Проверка активный юзер или нет"""
#     if not current_user.is_admin:
#         raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")
#     return current_user


# def get_superuser(current_user: Users = Security(get_current_user)):
#     """Проверка суперюзер или нет"""
#     if not current_user.is_superuser:
#         raise HTTPException(
#             status_code=400, detail="The user doesn't have enough privileges"
#         )
#     return current_user
