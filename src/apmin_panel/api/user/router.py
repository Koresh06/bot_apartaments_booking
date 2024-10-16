from typing import Annotated
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Form, Request

from src.apmin_panel.api.auth.permissions import get_current_user
from src.apmin_panel.api.auth.schemas import UserCreateInRegistration
from src.apmin_panel.api.auth.service import AuthApiRepo
from src.core.models.users import Users

from src.apmin_panel.conf_static import templates

from src.core.db_helper import get_db
from .service import UsersApiRepo
from .schemas import CreateAdminSchema


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get("/get-users/", response_class=HTMLResponse)
async def get_users(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Users = Depends(get_current_user),
    page: int = 1,
    size: int = 10,
):
    if not user:
        return RedirectResponse("/auth/", status_code=303)
    
    users = await UsersApiRepo(session).get_paginated_users(page, size)

    total_users = await UsersApiRepo(session).count_all_users()
    total_pages = (total_users + size - 1) // size

    if isinstance(users, str):
        return templates.TemplateResponse(
            request=request,
            name="users/get-users.html",
            context={
                "message": users,
                "user": user,
            },
        )

    return templates.TemplateResponse(
        request=request,
        name="users/get-users.html",
        context={
            "users": users,
            "user": user,
            "page": page,
            "total_pages": total_pages,
        },
    )


@router.get("/get-user-detail/{user_id}", response_class=HTMLResponse)
async def get_user_detail(
    user_id: int,    
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Users = Depends(get_current_user),
):
    if not user:
        return RedirectResponse("/auth/", status_code=303)
    
    user_by_id = await UsersApiRepo(session).get_user_by_id(user_id)

    if isinstance(user_by_id, str):
        return templates.TemplateResponse(
            request=request,
            name="users/get-users.html",
            context={
                "message": "user not found",
                "user": user,
            },
        )

    return templates.TemplateResponse(
        request=request,
        name="users/get-user-detail.html",
        context={
            "by_user": user_by_id,
            "user": user,
        },
    )


@router.get("/create-admin", response_class=HTMLResponse)
async def show_create_admin_form(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Users = Depends(get_current_user),
    message: str = None,
):
    if not user:
        return RedirectResponse("/auth/", status_code=303)
    
    not_landlords = await UsersApiRepo(session).get_users_not_admin()

    if isinstance(not_landlords, str):
        return templates.TemplateResponse(
            request=request,    
            name="users/create-admin.html",
            context={
                "message": not_landlords,
                "user": user,
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="users/create-admin.html",
        context={
            "users": not_landlords,
            "user": user,
            "message": message, 
        }
    )



@router.post("/submit-create-admin")
async def submit_create_admin(
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Users = Depends(get_current_user),
    schemas: CreateAdminSchema = Depends(CreateAdminSchema.as_form),
):
    if not user:
        return RedirectResponse("/auth/", status_code=303)
    
    admin = await AuthApiRepo(session).create_admin(schema=schemas)

    if not admin:
        return RedirectResponse("/users/create-admin?message=Не удалось создать админа.", status_code=303)

    return RedirectResponse("/users/create-admin?message=Админ успешно добавлен!", status_code=303)


@router.post("/{user_id}/banned")
async def banned_user(
    request: Request,
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Users = Depends(get_current_user),
):
    if not user:
        return RedirectResponse("/auth/", status_code=303)
    
    banned = await UsersApiRepo(session).banned_user_by_id(user_id)
    user_by_id = await UsersApiRepo(session).get_user_by_id(user_id)    

    if isinstance(user_by_id, str):
        return templates.TemplateResponse(
            request=request,
            name="users/get-user-detail.html",
            context={
                "message": user_by_id,
                "user": user,
            },
        )

    return templates.TemplateResponse(
        request=request, 
        name="users/get-user-detail.html",
        context={
            "by_user": user_by_id,
            "user": user,
        },
    )


@router.post("/{user_id}/unbanned")
async def unbanned_user(
    request: Request,
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Users = Depends(get_current_user),
):
    if not user:
        return RedirectResponse("/auth/", status_code=303)
    
    await UsersApiRepo(session).unbanned_user_by_id(user_id)
    user_by_id = await UsersApiRepo(session).get_user_by_id(user_id)    

    if isinstance(user_by_id, str):
        return templates.TemplateResponse(
            request=request,
            name="users/get-user-detail.html",
            context={
                "message": user_by_id,
                "user": user,
            },
        )

    return templates.TemplateResponse(
        request=request,
        name="users/get-user-detail.html",
        context={
            "by_user": user_by_id,
            "user": user,
        },
    )
