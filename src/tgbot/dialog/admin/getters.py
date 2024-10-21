from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import TextInput

from src.core.repo.requests import RequestsRepo


async def getter_name_city(dialog_manager: DialogManager, **kwargs, ) -> dict:
    name_city: TextInput = dialog_manager.find("name").get_value()
    
    return {"name": name_city}


async def getter_landlords(dialog_manager: DialogManager, **kwargs) -> dict:
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    landlords = await repo.admin_bot.get_landlords()
    dialog_manager.dialog_data["landlords"] = landlords
    return {"landlords": landlords}