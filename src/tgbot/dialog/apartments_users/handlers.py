from typing import Any

from aiogram.types import CallbackQuery

from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button

from src.core.repo.requests import RequestsRepo
from src.tgbot.dialog.apartments_users.states import FilteredCatalogApartmentsSG



async def handle_city_filter(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, item_id: str):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    list_citys = dialog_manager.dialog_data.get("citys")
    city = list_citys[int(item_id) - 1][0]  
    dialog_manager.dialog_data["city"] = city

    await dialog_manager.start(state=FilteredCatalogApartmentsSG.start, data={"city": city}, mode=StartMode.RESET_STACK)


async def handle_room_filter(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, item_id: str):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    list_rooms = dialog_manager.dialog_data.get("rooms")
    room = list_rooms[int(item_id) - 1][0]  
    dialog_manager.dialog_data["room"] = room

    await dialog_manager.start(state=FilteredCatalogApartmentsSG.start, data={"room": room}, mode=StartMode.RESET_STACK)


async def handle_confirm_min_max_price(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
    **_kwargs
):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    price_range = dialog_manager.dialog_data.get("price_range")

    await dialog_manager.start(state=FilteredCatalogApartmentsSG.start, data={"price_range": price_range}, mode=StartMode.RESET_STACK)



async def on_booking(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
    **_kwargs
):
    apartment = dialog_manager.dialog_data.get("apartment")
    
    