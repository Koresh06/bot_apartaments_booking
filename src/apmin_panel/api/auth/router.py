from typing import Annotated
from fastapi import BackgroundTasks, Response

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db_helper import get_db
from .schemas import UserCreateInRegistration, Token, LoginForm
from .service import AuthApiRepo
from .jwt import create_token
from src.apmin_panel.conf_static import templates
from src.core.config import config


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


@router.post("/access-token", response_model=Token)
async def login_access_token(
    response: Response,
    from_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
):
    """Авторизация пользователя"""
    user = await AuthApiRepo(session).authenticate(
        email=from_data.username,
        password=from_data.password,
    )

    if not user:
        return None
    
    token = create_token(user_id=user.id)

    return token


# @router.post("/registration")
# async def admin_registration(
#     session: Annotated[
#         AsyncSession,
#         Depends(get_db),
#     ],
#     new_admin: UserCreateInRegistration,
# ):
#     """Регистрация администратора"""
#     admin = await AuthApiRepo(session).create_admin(schema=new_admin)
#     if not admin:
#         raise HTTPException(status_code=400, detail="Не удалось создать админа.")
#     return admin


@router.get("/", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth.html",
    )


@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
):
    form = LoginForm(request=request)
    await form.create_oauth_form()

    validate_user_cookie = await login_access_token(
        response=Response(),
        from_data=form,
        session=session,
    )
    if validate_user_cookie is None:
        msg = "Неверное имя пользователя или пароль"
        # Возвращаем корректный ответ с кодом 400
        return templates.TemplateResponse(
            request=request,
            name="auth.html",
            context={"msg": msg},
        )

    response = RedirectResponse(url="/statistics/get-statistics/", status_code=status.HTTP_302_FOUND)

    response.set_cookie(
        key="access_token",
        value=validate_user_cookie["access_token"],
        httponly=True,
        expires=config.api.access_token_expire_minutes * 60,
    )

    return response



@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    msg = "Успешный выход из системы"
    response = templates.TemplateResponse(
            request=request,
            name="auth.html",
            context={"msg": msg},
        )

    response.delete_cookie(key="access_token")
    return response