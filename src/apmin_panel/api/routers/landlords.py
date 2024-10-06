from typing import Annotated
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request

from ..depandencies import admin_auth
from src.apmin_panel.conf_static import templates

from src.core.db_helper import db_helper
from src.apmin_panel.conf_static import templates

from ..services.landlord_api_service import LandlordApiRepo
from ..schemas.landlord_schemas import LandlordDateSchema


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
        Depends(db_helper.get_db),
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
        Depends(db_helper.get_db),
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


@router.post("/submit-statistics/")
async def statistics_landlord_date_by_id(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.get_db),
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

