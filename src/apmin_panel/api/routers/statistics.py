from typing import Annotated
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request

from src.apmin_panel.api.auth.permissions import get_current_user
from src.core.models.users import Users

from src.apmin_panel.conf_static import templates

from src.core.db_helper import get_db

from ..services.statistics_api_service import StatisticsApiRepo
from ..schemas.statistics_schemas import StatisticsDateSchema


router = APIRouter(
    prefix="/statistics",
    tags=["statistics"],
    responses={404: {"description": "Not found"}},
)


@router.get("/get-statistics/", response_class=HTMLResponse)
async def get_general_statistics(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    user: Users = Depends(get_current_user)
):
    if not user:
        return RedirectResponse("/auth/", status_code=303)
    
    general_statistics = await StatisticsApiRepo(session).get_general_statistics()

    if isinstance(general_statistics, str):
        return templates.TemplateResponse(
            request=request,
            name="statistics/general-statistics.html",
            context={
                "message": general_statistics,
                "user": user,
            })
    
    return templates.TemplateResponse(
        request=request,
        name="statistics/general-statistics.html",
        context={
            "statistics": general_statistics,
            "user": user,
        },
    )


@router.post("/submit-general-statistics/")
async def general_statistics_date(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    user: Users = Depends(get_current_user),
    date_data: StatisticsDateSchema = Depends(StatisticsDateSchema.as_form),
):
    if not user:
        return RedirectResponse("/auth/", status_code=303)
    
    general_statistics = await StatisticsApiRepo(session).get_general_statistics(
        start_date=date_data.start_date,
        end_date=date_data.end_date,
    )
    
    if isinstance(general_statistics, str):
        return templates.TemplateResponse(
            request=request,
            name="statistics/general-statistics.html",
            context={
                "message": general_statistics,
                "user": user,
            })
    
    return templates.TemplateResponse(
        request=request,
        name="statistics/general-statistics.html",
        context={
            "statistics": general_statistics,
            "user": user,
            "start_date": date_data.start_date,
            "end_date": date_data.end_date,
        },
    )


@router.get("/pending-bookings", response_class=HTMLResponse)
async def get_completed_bookings(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    user: Users = Depends(get_current_user),
):
    if not user:
        return RedirectResponse("/auth/", status_code=303)
    
    pending_bookings = await StatisticsApiRepo(session).get_pending_bookings()
    print(pending_bookings)

    if isinstance(pending_bookings, str):
        return templates.TemplateResponse(
            request=request,
            name="statistics/pending-bookings.html",
            context={
                "message": pending_bookings,
                "user": user,
            })
    
    return templates.TemplateResponse(
        request=request,
        name="statistics/pending-bookings.html",
        context={
            "bookings": pending_bookings,
            "user": user,
        },
    )


@router.get("/completed-bookings", response_class=HTMLResponse)
async def get_completed_bookings(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    user: Users = Depends(get_current_user),
):
    if not user:
        return RedirectResponse("/auth/", status_code=303)
    
    completed_bookings = await StatisticsApiRepo(session).get_completed_bookings()

    if isinstance(completed_bookings, str):
        return templates.TemplateResponse(
            request=request,
            name="statistics/completed-bookings.html",
            context={
                "message": completed_bookings,
                "user": user,
            })
    
    return templates.TemplateResponse(
        request=request,
        name="statistics/completed-bookings.html",
        context={
            "bookings": completed_bookings,
            "user": user,
        },
    )


@router.get("/total-income-bookings", response_class=HTMLResponse)
async def get_total_income_bookings(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    user: Users = Depends(get_current_user),
):
    if not user:
        return RedirectResponse("/auth/", status_code=303)
    
    total_income_bookings = await StatisticsApiRepo(session).get_total_income_bookings()

    if isinstance(total_income_bookings, str):
        return templates.TemplateResponse(
            request=request,
            name="statistics/total-income-bookings.html",
            context={
                "message": total_income_bookings,
                "user": user,
            })
    
    return templates.TemplateResponse(
        request=request,
        name="statistics/total-income-bookings.html",
        context={
            "bookings": total_income_bookings,
            "user": user,
        },
    )
