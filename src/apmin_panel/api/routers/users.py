from typing import Annotated
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request

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
    session: Annotated[
        AsyncSession,
        Depends(get_db)],
    is_authenticated: bool = Depends(admin_auth),
):
    users = await UsersApiRepo(session).get_all_users()

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
        },
    )


@router.get("/get-user-detail/{user_id}", response_class=HTMLResponse)
async def get_user_detail(
    user_id: int,    
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    is_authenticated: bool = Depends(admin_auth),
):
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


@router.post("/{user_id}/banned")
async def banned_user(
    request: Request,
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    is_authenticated: bool = Depends(admin_auth),
):
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
