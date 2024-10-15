from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from ..auth_helpers import (
    create_hashed_cookie,
)
from ..depandencies import check_admin_auth
from ..schemas.auth_schemas import LoginData
from src.apmin_panel.conf_static import templates

from src.core.config import config


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="admin/login")


@router.get("/login", response_class=HTMLResponse)
async def login_form(
    request: Request,
    is_authenticated: bool = Depends(check_admin_auth),
):
    return templates.TemplateResponse(
        request=request,
        name="auth.html",
        context={"user": is_authenticated},
    )


@router.post("/login")
async def login(
    request: Request,
    login_data: LoginData = Depends(LoginData.as_form),
):
    try:
        if not (login_data.username == config.api.superuser_login and login_data.password == config.api.superuser_password) and not (login_data.username == config.api.admin_login and login_data.password == config.api.admin_password):
            msg = "Неверное имя пользователя или пароль"
            return templates.TemplateResponse(
                request=request,
                name="auth.html",
                context={"msg": msg},
            )
        else:
            hashed_cookie = create_hashed_cookie(login_data.username, config.api.secret_key)

            role = "superuser" if login_data.username == config.api.superuser_login and login_data.password == config.api.superuser_password else "admin"
        
            response = RedirectResponse(url="/statistics/get-statistics/", status_code=status.HTTP_302_FOUND)

            response.set_cookie(
                key="admin_token", value=hashed_cookie, httponly=True, max_age=1800
            )
            response.set_cookie(
                key="user_role", value=role, httponly=True, max_age=1800
            )
        return response
    except HTTPException:
        msg = "Unknown Error"
        return templates.TemplateResponse(
            request=request,
            name="auth.html",
            context={"msg": msg},
        )


@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    msg = "Успешный выход из системы"
    response = templates.TemplateResponse(
            request=request,
            name="auth.html",
            context={"msg": msg},
        )

    response.delete_cookie(key="admin_token")
    return response