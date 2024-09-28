from aiogram_dialog import DialogManager
from aiogram.types import User
from aiogram_dialog.widgets.input import TextInput, MessageInput

from src.core.config import settings
from src.core.models import Landlords
from src.core.repo.requests import RequestsRepo


async def start_getters(
    dialog_manager: DialogManager,
    event_from_user: User,
    **kwargs,
):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    check_landlord: Landlords = await repo.bot_apartments.check_landlord(
        dialog_manager.event.from_user.id
    )

    return {"landlord": check_landlord, "not_landlord": not check_landlord}


async def getter_information_registration(dialog_manager: DialogManager, **kwargs):
    name: TextInput = dialog_manager.find("name").get_value()
    phone: TextInput = dialog_manager.find("phone").get_value()

    return {
        "name": name,
        "phone": phone,
    }
