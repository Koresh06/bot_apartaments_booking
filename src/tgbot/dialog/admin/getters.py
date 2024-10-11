from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import TextInput


async def getter_name_city(dialog_manager: DialogManager, **kwargs, ) -> dict:
    name_city: TextInput = dialog_manager.find("name").get_value()
    
    return {"name": name_city}