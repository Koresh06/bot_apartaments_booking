from typing import Annotated
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request

from ..depandencies import admin_auth
from src.apmin_panel.conf_static import templates

from src.core.db_helper import get_db

from ..services.landlord_api_service import LandlordApiRepo
from ..schemas.landlord_schemas import CreateLandlordSchema, LandlordDateSchema


router = APIRouter(
    prefix="/landlord",
    tags=["landlord"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(admin_auth)],
)


@router.get("/get-landlords", response_class=HTMLResponse)
async def get_landlords(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    is_authenticated: bool = Depends(admin_auth),
):
    landlords = await LandlordApiRepo(session).get_all_landlords()

    if isinstance(landlords, str):
        return templates.TemplateResponse(
            "landlord/get-landlords.html",
            {
                "request": request,
                "message": landlords,
            },
        )

    return templates.TemplateResponse(
        "landlord/get-landlords.html",
        {
            "request": request,
            "landlords": landlords,
            "user": is_authenticated,
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
    is_authenticated: bool = Depends(admin_auth),
):
    statistics = await LandlordApiRepo(session).get_statistics_by_landlord_id(
        landlord_id=landlord_id,
    )
    if isinstance(statistics, str):
        return templates.TemplateResponse(
            "landlord/statistics.html",
            {
                "request": request,
                "message": statistics,
            },
        )

    return templates.TemplateResponse(
        "landlord/statistics.html",
        {
            "request": request,
            "statistics": statistics,
            "user": is_authenticated,
        },
    )


@router.post("/submit-landlord-statistics/")
async def statistics_landlord_date_by_id(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    is_authenticated: bool = Depends(admin_auth),
    date_data: LandlordDateSchema = Depends(LandlordDateSchema.as_form),
):
    statistics = await LandlordApiRepo(session).get_statistics_by_landlord_id(
        landlord_id=date_data.landlord_id,
        start_date=date_data.start_date,
        end_date=date_data.end_date,
    )
    if isinstance(statistics, str):
        return templates.TemplateResponse(
            "landlord/statistics.html",
            {
                "request": request,
                "message": statistics,
            },
        )

    return templates.TemplateResponse(
        "landlord/statistics.html",
        {
            "request": request,
            "statistics": statistics,
            "user": is_authenticated,
            "start_date": date_data.start_date,
            "end_date": date_data.end_date,
        },
    )


@router.get("/{landlord_id}/completed-bookings", response_class=HTMLResponse)
async def get_completed_bookings(
    request: Request,
    landlord_id: int,
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    is_authenticated: bool = Depends(admin_auth),
):
    completed_bookings = await LandlordApiRepo(
        session
    ).get_completed_bookings_by_landlord_id(landlord_id)

    if isinstance(completed_bookings, str):
        return templates.TemplateResponse(
            "statistics/completed-bookings.html",
            {
                "request": request,
                "message": completed_bookings,
            },
        )

    return templates.TemplateResponse(
        "statistics/completed-bookings.html",
        {
            "request": request,
            "bookings": completed_bookings,
            "user": is_authenticated,
        },
    )


@router.get("/{landlord_id}/pending-bookings", response_class=HTMLResponse)
async def get_completed_bookings(
    request: Request,
    landlord_id: int,
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    is_authenticated: bool = Depends(admin_auth),
):
    pending_bookings = await LandlordApiRepo(
        session
    ).get_pending_bookings_by_landlord_id(landlord_id)

    if isinstance(pending_bookings, str):
        return templates.TemplateResponse(
            "statistics/pending-bookings.html",
            {
                "request": request,
                "message": pending_bookings,
            },
        )

    return templates.TemplateResponse(
        "statistics/pending-bookings.html",
        {
            "request": request,
            "bookings": pending_bookings,
            "user": is_authenticated,
        },
    )


@router.get("/{landlord_id}/total-income-bookings", response_class=HTMLResponse)
async def get_total_income_bookings(
    request: Request,
    landlord_id: int,
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    is_authenticated: bool = Depends(admin_auth),
):
    total_income_bookings = await LandlordApiRepo(
        session
    ).get_total_income_bookings_by_landlord_id(landlord_id)

    if isinstance(total_income_bookings, str):
        return templates.TemplateResponse(
            "statistics/total-income-bookings.html",
            {
                "request": request,
                "message": total_income_bookings,
            },
        )

    return templates.TemplateResponse(
        "statistics/total-income-bookings.html",
        {
            "request": request,
            "bookings": total_income_bookings,
            "user": is_authenticated,
        },
    )


@router.get("/create-landlord", response_class=HTMLResponse)
async def show_create_landlord_form(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    is_authenticated: bool = Depends(admin_auth),
    message: str = None,  # Добавлен параметр для сообщения
):
    not_landlords = await LandlordApiRepo(session).get_users_not_landlord()

    if isinstance(not_landlords, str):
        return templates.TemplateResponse(
            "landlord/create-landlord.html",
            {
                "request": request,
                "message": not_landlords,
            },
        )

    return templates.TemplateResponse(
        "landlord/create-landlord.html",
        {
            "request": request,
            "users": not_landlords,
            "user": is_authenticated,
            "message": message,  # Передаем сообщение в шаблон
        },
    )


@router.post("/submit-create-landlord")
async def submit_create_landlord(
    session: Annotated[AsyncSession, Depends(get_db)],
    create_landlord: CreateLandlordSchema = Depends(CreateLandlordSchema.as_form),
    is_authenticated: bool = Depends(admin_auth),
):
    landlord = await LandlordApiRepo(session).create_landlord(create_landlord)
    
    if not landlord:
        # Если не удалось создать, перенаправляем с сообщением об ошибке
        return RedirectResponse("/landlord/create-landlord?message=Не удалось создать арендодателя.", status_code=303)

    # Если успешно создан, перенаправляем с сообщением об успехе
    return RedirectResponse("/landlord/create-landlord?message=Арендодатель успешно добавлен!", status_code=303)

