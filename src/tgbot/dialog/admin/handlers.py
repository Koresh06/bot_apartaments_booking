from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput

from src.core.repo.requests import RequestsRepo
from .states import MainAdminSG


async def handle_register_name_city(callback: CallbackQuery, widget: ManagedTextInput, dialog_manager: DialogManager):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    name_city: TextInput = dialog_manager.find("name").get_value()

    city = await repo.admin.register_name_city(name=name_city)
    if city:
        await callback.answer(text="Поздравляем! ✅ Город зарегистрирован!")
        await dialog_manager.start(state=MainAdminSG.start, mode=StartMode.RESET_STACK)
    else:
        await callback.answer(text="Что-то пошло не так, попробуйте еще раз")