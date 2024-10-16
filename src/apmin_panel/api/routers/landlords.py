import logging
from typing import Annotated
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Request

from src.apmin_panel.api.auth.permissions import get_current_user
from src.core.models.users import Users

from src.apmin_panel.conf_static import templates

from src.core.db_helper import get_db

from ..services.landlord_api_service import LandlordApiRepo
from ..schemas.landlord_schemas import CreateLandlordSchema, LandlordDateSchema


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/landlord",
    tags=["landlord"],
    responses={404: {"description": "Not found"}},
)


@router.get("/get-landlords", response_class=HTMLResponse)
async def get_landlords(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    user: Users = Depends(get_current_user),
    page: int = 1,
    size: int = 10,
):
    if not user:
        return RedirectResponse("/auth/", status_code=303)
    
    landlords = await LandlordApiRepo(session).get_paginated_landlords(page, size)

    total_landlords = await LandlordApiRepo(session).count_all_landlords()
    total_pages = (total_landlords + size - 1) // size

    if isinstance(landlords, str):
        return templates.TemplateResponse(
            request=request,
            name="landlord/get-landlords.html",
            context={
                "message": landlords,
                "user": user,
            })

    return templates.TemplateResponse(
        request=request,
        name="landlord/get-landlords.html",
        context={
            "landlords": landlords,
            "user": user,
            "page": page,
            "total_pages": total_pages,
        },
    )


@router.get("/statistics/{landlord_id}", response_class=HTMLResponse)
async def statistics_landlord_by_id(
    request: Request,
    landlord_id: int,
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    user: Users = Depends(get_current_user),
):
    if not user:
        return RedirectResponse("/auth/", status_code=303)
    
    statistics = await LandlordApiRepo(session).get_statistics_by_landlord_id(
        landlord_id=landlord_id,
    )
    if isinstance(statistics, str):
        return templates.TemplateResponse(
            request=request,
            name="landlord/statistics.html",
            context={
                "message": statistics,
                "user": user,
            })

    return templates.TemplateResponse(
        request=request,
        name="landlord/statistics.html",
        context={
            "statistics": statistics,
            "user": user,
        },
    )


@router.post("/submit-landlord-statistics/")
async def statistics_landlord_date_by_id(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    user: Users = Depends(get_current_user),
    date_data: LandlordDateSchema = Depends(LandlordDateSchema.as_form),
):
    if not user:
        return RedirectResponse("/auth/", status_code=303)
    
    statistics = await LandlordApiRepo(session).get_statistics_by_landlord_id(
        landlord_id=date_data.landlord_id,
        start_date=date_data.start_date,
        end_date=date_data.end_date,
    )
    if isinstance(statistics, str):
        return templates.TemplateResponse(
            request=request,
            name="landlord/statistics.html",
            context={
                "message": statistics,
                "user": user,
            })

    return templates.TemplateResponse(
        request=request,
        name="landlord/statistics.html",
        context={
            "statistics": statistics,
            "user": user,
            "start_date": date_data.start_date,
            "end_date": date_data.end_date,
        },
    )


@router.get("/{landlord_id}/pending-bookings", response_class=HTMLResponse)
async def get_pending_bookings(
    request: Request,
    landlord_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Users = Depends(get_current_user),
):
    if not user:
        return RedirectResponse("/auth/", status_code=303)

    pending_bookings = await LandlordApiRepo(session).get_pending_bookings_by_landlord_id(landlord_id)
    logger.info(f"Получены ожидающие бронирования: {pending_bookings}")
    
    if not pending_bookings:
        return templates.TemplateResponse(
            request=request,
            name="statistics/pending-bookings.html",
            context={
                "message": "Нет ожидающих бронирований.",
                "user": user,
            },
        )
    return templates.TemplateResponse(
        request=request,
        name="statistics/pending-bookings.html",
        context={
            "bookings": pending_bookings,
            "user": user,
        },
    )


@router.get("/{landlord_id}/completed-bookings", response_class=HTMLResponse)
async def get_completed_bookings(
    request: Request,
    landlord_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Users = Depends(get_current_user),
):
    if not user:
        return RedirectResponse("/auth/", status_code=303)

    completed_bookings = await LandlordApiRepo(session).get_completed_bookings_by_landlord_id(landlord_id)
    logger.info(f"Получены завершенные бронирования: {completed_bookings}")

    if not completed_bookings:
        return templates.TemplateResponse(
            request=request,
            name="statistics/completed-bookings.html",
            context={
                "message": "Нет завершенных бронирований.",
                "user": user,
            },
        )

    return templates.TemplateResponse(
        request=request,
        name="statistics/completed-bookings.html",
        context={
            "bookings": completed_bookings,
            "user": user,
        },
    )


@router.get("/{landlord_id}/total-income-bookings", response_class=HTMLResponse)
async def get_total_income_bookings(
    request: Request,
    landlord_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Users = Depends(get_current_user),
):
    if not user:
        return RedirectResponse("/auth/", status_code=303)

    total_income_bookings = await LandlordApiRepo(session).get_total_income_bookings_by_landlord_id(landlord_id)
    logger.info(f"Получен общий доход от бронирований для арендатора {landlord_id}: {total_income_bookings}")

    if isinstance(total_income_bookings, str):
        return templates.TemplateResponse(
            request=request,
            name="statistics/total-income-bookings.html",
            context={
                "message": total_income_bookings,
                "user": user,
            }
        )
    return templates.TemplateResponse(
        request=request,
        name="statistics/total-income-bookings.html",
        context={
            "bookings": total_income_bookings,
            "user": user,
        }
    )



@router.get("/create-landlord", response_class=HTMLResponse)
async def show_create_landlord_form(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Users = Depends(get_current_user),
    message: str = None,
):
    if not user:
        return RedirectResponse("/auth/", status_code=303)
    
    not_landlords = await LandlordApiRepo(session).get_users_not_landlord()
    if isinstance(not_landlords, str):
        return templates.TemplateResponse(
            request=request,    
            name="landlord/create-landlord.html",
            context={
                "message": not_landlords,
                "user": user,
            })

    return templates.TemplateResponse(
        request=request,
        name="landlord/create-landlord.html",
        context={
            "users": not_landlords,
            "user": user,
            "message": message, 
        },
    )


@router.post("/submit-create-landlord")
async def submit_create_landlord(
    session: Annotated[AsyncSession, Depends(get_db)],
    from_data: CreateLandlordSchema = Depends(CreateLandlordSchema.as_form),
    user: Users = Depends(get_current_user),
):
    if not user:
        return RedirectResponse("/auth/", status_code=303)
    
    landlord = await LandlordApiRepo(session).create_landlord(from_data)
    
    if not landlord:
        return RedirectResponse("/landlord/create-landlord?message=Не удалось создать арендодателя.", status_code=303)

    return RedirectResponse("/landlord/create-landlord?message=Арендодатель успешно добавлен!", status_code=303)

