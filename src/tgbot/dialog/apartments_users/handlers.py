from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode, ShowMode
from aiogram_dialog.widgets.kbd import Button

from src.core.repo.requests import RequestsRepo
from src.tgbot.dialog.apartments_users.states import FilteredCatalogApartmentsSG
from src.tgbot.dialog.booking_apartment.states import BookingApartmentSG

from src.core.models import Landlords


async def handle_city_filter(
    callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, item_id: str
):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")

    dialog_manager.dialog_data["city_id"] = item_id

    count = await repo.filter_apartments.no_data_on_apartments(city_id=int(item_id))
    dialog_manager.dialog_data["count"] = count 

    await dialog_manager.next()


async def handle_confirm_min_max_price(
    callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, **_kwargs
):
    price_range = dialog_manager.dialog_data.get("price_range")
    dialog_manager.dialog_data["price_range"] = price_range

    await dialog_manager.next()


async def handle_room_filter(
    callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, item_id: str
):
    city_id = dialog_manager.dialog_data.get("city_id")
    price_range = dialog_manager.dialog_data.get("price_range")
    
    rooms = dialog_manager.dialog_data.get("rooms")
    room = rooms[int(item_id) - 1][0]

    await dialog_manager.start(
        state=FilteredCatalogApartmentsSG.start,
        data={
            "city_id": city_id,
            "price_range": price_range,
            "room": room,
        },
        mode=StartMode.RESET_STACK,
    )


async def on_phone(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, **_kwargs):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")

    landlord: Landlords = dialog_manager.dialog_data.get("apartment")["landlord"]
    await repo.filter_apartments.add_phone_click(landlord_id=landlord.id)

    await callback.answer(
        text=f"🏠 Арендодатель: {landlord.company_name}\n📞 Номер телефона: {landlord.phone}",
        show_alert=True
    )


async def on_booking(
    callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, **_kwargs
):
    apartment = dialog_manager.dialog_data.get("apartment")
    city_id = dialog_manager.start_data.get("city_id")
    price_range = dialog_manager.start_data.get("price_range")
    room = dialog_manager.start_data.get("room")

    await dialog_manager.start(
        state=BookingApartmentSG.start_date,
        data={
            "apartment": apartment,
            "city_id": city_id,
            "price_range": price_range,
            "room": room
        },
        mode=StartMode.NORMAL,
    )



async def handle_landlord_info(
    callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, **_kwargs
    ):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")

    apartment_id = dialog_manager.dialog_data.get("apartment")["apartment_id"]
    await repo.filter_apartments.update_click_contact_apartment(apartment_id=apartment_id)
    
    await dialog_manager.switch_to(state=FilteredCatalogApartmentsSG.landlord_info, show_mode=ShowMode.EDIT)

    
