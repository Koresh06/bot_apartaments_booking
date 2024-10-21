from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Button

from src.core.repo.requests import RequestsRepo
from .states import MainAdminSG


async def handle_register_name_city(
    callback: CallbackQuery, widget: ManagedTextInput, dialog_manager: DialogManager
):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    name_city: TextInput = dialog_manager.find("name").get_value()

    city = await repo.admin_bot.register_name_city(name=name_city)
    if city:
        await callback.answer(text="Поздравляем! ✅ Город зарегистрирован!")
        await dialog_manager.start(state=MainAdminSG.start, mode=StartMode.RESET_STACK)
    else:
        await callback.answer(text="Что-то пошло не так, попробуйте еще раз")


async def handle_register_apartament_by_landlord(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
    item_id: str,
):
    list_landlords = dialog_manager.dialog_data.get("landlords")
    dialog_manager.dialog_data["landlord_id"] = item_id
    data = dict(list_landlords)
    name = data.get(int(item_id))

    dialog_manager.dialog_data["name"] = name

    await dialog_manager.next()


async def admin_confirm_deteils_apartment_landlord(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    
    landlord_id = dialog_manager.dialog_data.get("landlord_id")
    name = dialog_manager.dialog_data.get("name")

    data = {
        "city_id": dialog_manager.dialog_data["city_id"],
        "street": dialog_manager.find("street").get_value(),
        "house_number": dialog_manager.find("house_number").get_value(),
        "apartment_number": dialog_manager.find("apartment_number").get_value(),
        "price_per_day": dialog_manager.find("price_per_day").get_value(),
        "rooms": dialog_manager.find("rooms").get_value(),
        "description": dialog_manager.find("description").get_value(),
        "photos": dialog_manager.dialog_data.get("photos", []),
    }

    if await repo.admin_bot.admin_register_apartment_landlord(landlord_id=int(landlord_id), data=data):
        await callback.answer(text=f"Поздравляем! ✅ Апартамент для арендодателя - {name} зарегистрирован!", show_alert=True)
        await dialog_manager.done()
    else:
        await callback.answer(text="Что-то пошло не так, попробуйте еще раз", show_alert=True)