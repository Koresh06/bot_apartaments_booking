from typing import Annotated
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request

from ..depandencies import admin_auth
from src.apmin_panel.conf_static import templates

from src.core.db_helper import db_helper

from ..services.statistics_api_service import StatisticsApiRepo
from ..schemas.statistics_schemas import StatisticsDateSchema


router = APIRouter(
    prefix="/statistics",
    tags=["statistics"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(admin_auth)],
)


@router.get("/get-statistics/", response_class=HTMLResponse)
async def get_general_statistics(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.get_db),
    ],
    is_authenticated: bool = Depends(admin_auth),
):
    general_statistics = await StatisticsApiRepo(session).get_general_statistics()

    if isinstance(general_statistics, str):
        return templates.TemplateResponse(
            "statistics/general-statistics.html",
            {
                "request": request,
                "message": general_statistics,
            },
        )
    
    return templates.TemplateResponse(
        "statistics/general-statistics.html",
        {
            "request": request,
            "statistics": general_statistics,
            "user": is_authenticated,
        },
    )


@router.post("/submit-general-statistics/")
async def general_statistics_date(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.get_db),
    ],
    is_authenticated: bool = Depends(admin_auth),
    date_data: StatisticsDateSchema = Depends(StatisticsDateSchema.as_form),
):
    general_statistics = await StatisticsApiRepo(session).get_general_statistics(
        start_date=date_data.start_date,
        end_date=date_data.end_date,
    )
    
    if isinstance(general_statistics, str):
        return templates.TemplateResponse(
            "statistics/general-statistics.html",
            {
                "request": request,
                "message": general_statistics,
            },
        )
    
    return templates.TemplateResponse(
        "statistics/general-statistics.html",
        {
            "request": request,
            "statistics": general_statistics,
            "user": is_authenticated,
            "start_date": date_data.start_date,
            "end_date": date_data.end_date,
        },
    )


@router.get("/pending-bookings", response_class=HTMLResponse)
async def get_completed_bookings(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.get_db),
    ],
    is_authenticated: bool = Depends(admin_auth),
):
    pending_bookings = await StatisticsApiRepo(session).get_pending_bookings()

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


@router.get("/completed-bookings", response_class=HTMLResponse)
async def get_completed_bookings(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.get_db),
    ],
    is_authenticated: bool = Depends(admin_auth),
):
    completed_bookings = await StatisticsApiRepo(session).get_completed_bookings()

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


@router.get("/total-income-bookings", response_class=HTMLResponse)
async def get_total_income_bookings(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.get_db),
    ],
    is_authenticated: bool = Depends(admin_auth),
):
    total_income_bookings = await StatisticsApiRepo(session).get_total_income_bookings()

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
