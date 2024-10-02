from aiogram.types import CallbackQuery

from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button

from src.tgbot.dialog.apartments_users.states import FilteredCatalogApartmentsSG
from src.tgbot.dialog.booking_apartment.states import BookingApartmentSG



async def handle_city_filter(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, item_id: str):
    list_citys = dialog_manager.dialog_data.get("citys")
    city_id = list_citys[int(item_id) - 1][1]  
    dialog_manager.dialog_data["city_id"] = city_id

    await dialog_manager.start(state=FilteredCatalogApartmentsSG.start, data={"city_id": city_id, "price_range": None, "rooms": None}, mode=StartMode.RESET_STACK)


async def handle_room_filter(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, item_id: str):
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
    price_range = dialog_manager.dialog_data.get("price_range")

    await dialog_manager.start(state=FilteredCatalogApartmentsSG.start, data={"price_range": price_range}, mode=StartMode.RESET_STACK)



async def on_booking(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
    **_kwargs
):
    apartment = dialog_manager.dialog_data.get("apartment")

    await dialog_manager.start(state=BookingApartmentSG.start_date, data={"apartment": apartment}, mode=StartMode.NORMAL)
    
    