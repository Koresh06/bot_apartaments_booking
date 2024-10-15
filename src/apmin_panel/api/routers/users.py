from pydantic import Field
from typing import Annotated
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Form, Request

from ..depandencies import admin_auth
from src.apmin_panel.conf_static import templates

from src.core.db_helper import get_db

from ..services.users_api_service import UsersApiRepo


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
    # dependencies=[Depends(admin_auth)],
)


@router.get("/get-users/", response_class=HTMLResponse)
async def get_users(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    is_authenticated: bool = Depends(admin_auth),
    page: int = 1,
    size: int = 10,
):
    if not is_authenticated:
        return RedirectResponse("/auth/login", status_code=303)
    
    users = await UsersApiRepo(session).get_paginated_users(page, size)

    total_users = await UsersApiRepo(session).count_all_users()
    total_pages = (total_users + size - 1) // size

    if isinstance(users, str):
        return templates.TemplateResponse(
            request=request,
            name="users/get-users.html",
            context={"message": users},
        )

    return templates.TemplateResponse(
        request=request,
        name="users/get-users.html",
        context={
            "users": users,
            "user": is_authenticated,
            "page": page,
            "total_pages": total_pages,
        },
    )


@router.get("/get-user-detail/{user_id}", response_class=HTMLResponse)
async def get_user_detail(
    user_id: int,    
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    is_authenticated: bool = Depends(admin_auth),
):
    if not is_authenticated:
        return RedirectResponse("/auth/login", status_code=303)
    
    user_by_id = await UsersApiRepo(session).get_user_by_id(user_id)

    if isinstance(user_by_id, str):
        return templates.TemplateResponse(
            request=request,
            name="users/get-users.html",
            context={"message": "user not found"},
        )

    return templates.TemplateResponse(
        request=request,
        name="users/get-user-detail.html",
        context={
            "by_user": user_by_id,
            "user": is_authenticated,
        },
    )


@router.get("/create-admin", response_class=HTMLResponse)
async def show_create_admin_form(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    is_authenticated: bool = Depends(admin_auth),
    message: str = None,
):
    if not is_authenticated:
        return RedirectResponse("/auth/login", status_code=303)
    
    not_landlords = await UsersApiRepo(session).get_users_not_admin()

    if isinstance(not_landlords, str):
        return templates.TemplateResponse(
            request=request,    
            name="users/create-admin.html",
            context={"message": not_landlords})

    return templates.TemplateResponse(
        request=request,
        name="users/create-admin.html",
        context={
            "users": not_landlords,
            "user": is_authenticated,
            "message": message, 
        },
    )


@router.post("/submit-create-admin")
async def submit_create_admin(
    session: Annotated[AsyncSession, Depends(get_db)],
    user_id: int = Form(...),
    is_authenticated: bool = Depends(admin_auth),
):
    if not is_authenticated:
        return RedirectResponse("/auth/login", status_code=303)
    
    admin = await UsersApiRepo(session).create_admin(user_id)

    if not admin:
        return RedirectResponse("/users/create-admin?message=Не удалось создать админа.", status_code=303)

    return RedirectResponse("/users/create-admin?message=Админ успешно добавлен!", status_code=303)


@router.post("/{user_id}/banned")
async def banned_user(
    request: Request,
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    is_authenticated: bool = Depends(admin_auth),
):
    if not is_authenticated:
        return RedirectResponse("/auth/login", status_code=303)
    
    banned = await UsersApiRepo(session).banned_user_by_id(user_id)
    user_by_id = await UsersApiRepo(session).get_user_by_id(user_id)    

    if isinstance(user_by_id, str):
        return templates.TemplateResponse(
            request=request,
            name="users/get-user-detail.html",
            context={"message": user_by_id},
        )

    return templates.TemplateResponse(
        request=request, 
        name="users/get-user-detail.html",
        context={
            "by_user": user_by_id,
            "user": is_authenticated,
        },
    )


@router.post("/{user_id}/unbanned")
async def unbanned_user(
    request: Request,
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    is_authenticated: bool = Depends(admin_auth),
):
    if not is_authenticated:
        return RedirectResponse("/auth/login", status_code=303)
    
    await UsersApiRepo(session).unbanned_user_by_id(user_id)
    user_by_id = await UsersApiRepo(session).get_user_by_id(user_id)    

    if isinstance(user_by_id, str):
        return templates.TemplateResponse(
            request=request,
            name="users/get-user-detail.html",
            context={"message": user_by_id},
        )

    return templates.TemplateResponse(
        request=request,
        name="users/get-user-detail.html",
        context={
            "by_user": user_by_id,
            "user": is_authenticated,
        },
    )
