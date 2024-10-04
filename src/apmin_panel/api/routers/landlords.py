from typing import Annotated
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request

from ..depandencies import admin_auth
from src.apmin_panel.conf_static import templates

from src.core.db_helper import db_helper
from src.apmin_panel.conf_static import templates

from ..services.landlord_api_service import LandlordApiRepo


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