from typing import Annotated
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request

from src.apmin_panel.api.auth.permissions import get_current_user
from src.apmin_panel.api.landlord.service import LandlordApiRepo
from src.core.models.users import Users

from src.apmin_panel.conf_static import templates

from src.core.db_helper import get_db
from .service import ApartmentApiRepo



router = APIRouter(
    prefix="/apartment",
    tags=["apartment"],
    responses={404: {"description": "Not found"}},
)


@router.get("/get-apartments", response_class=JSONResponse)
async def get_apartments(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Users = Depends(get_current_user),
    page: int = 1,
    size: int = 10,
):
    if not user:
        return RedirectResponse("/auth/", status_code=303)
    
    apartments = await ApartmentApiRepo(session).get_paginated_apartments(page, size)

    total_apartments = await ApartmentApiRepo(session).count_all_apartments()
    total_pages = (total_apartments + size - 1) // size

    if isinstance(apartments, str):
        return templates.TemplateResponse(
            request=request,
            name="apartments/get-apartments.html",
            context={
                "message": apartments,
                "user": user,
            },
        )
    
    return templates.TemplateResponse(
        request=request,
        name="apartments/get-apartments.html",
        context={
            "apartments": apartments,
            "user": user,
            "page": page,
            "total_pages": total_pages,
        },
    )
    
    
@router.get("/get-apartments-landlord/{landlord_id}", response_class=HTMLResponse)
async def get_apartment(
    request: Request,
    landlord_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Users = Depends(get_current_user),
):
    apartments = await ApartmentApiRepo(session).get_apartment_by_landlord(landlord_id)
    landlord = await ApartmentApiRepo(session).get_landlord_by_id(landlord_id)

    
    if isinstance(apartments, str):
        return templates.TemplateResponse(
            request=request,
            name="apartments/get-apatments-landlord.html",
            context={
                "message": apartments,
                "user": user,
            },
        )
    
    return templates.TemplateResponse(
        request=request,
        name="apartments/get-apatments-landlord.html",
        context={
            "apartments": apartments,
            "landlord": landlord,
            "user": user,
        },
    )


    