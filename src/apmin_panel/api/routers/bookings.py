from typing import Annotated
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request

from ..depandencies import admin_auth
from src.apmin_panel.conf_static import templates

from src.core.db_helper import get_db

from ..services.booking_api_service import BookingApiRepo


router = APIRouter(
    prefix="/booking",
    tags=["booking"],
    responses={404: {"description": "Not found"}},
    # dependencies=[Depends(admin_auth)],
)


@router.get("/get-bookings/", response_class=HTMLResponse)
async def get_bookings(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    is_authenticated: bool = Depends(admin_auth),
    page: int = 1,
    size: int = 10,
):
    if not is_authenticated:
        return RedirectResponse("/auth/login", status_code=303)
    
    bookings = await BookingApiRepo(session).get_paginated_bookings(page, size)

    total_bookings = await BookingApiRepo(session).count_all_bookings()
    total_pages = (total_bookings + size - 1) // size

    if isinstance(bookings, str):
        return templates.TemplateResponse(
            request=request,
            name="bookings.html",
            context={
                "message": bookings,
                "user": is_authenticated,
            })

    return templates.TemplateResponse(
        request=request,
        name="bookings.html",
        context={
            "bookings": bookings,
            "user": is_authenticated,
            "page": page,
            "total_pages": total_pages
        },
    )
