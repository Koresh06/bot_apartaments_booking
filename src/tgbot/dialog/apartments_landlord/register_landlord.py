from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, Next, Back
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput


from src.tgbot.bot import dp
from .getters import getter_information_registration
from .handlers import (
    error_phone_handler,
    confirm_landlord_handler,
    error_handler,
    
)

from src.core.repo.requests import RequestsRepo
from ..apartments_landlord.states import LandlordStateSG, MenuLandlordSG



register_landlord_dialog = Dialog(
    Window(
        Const(text="Для дальнейшей работы необходимо проqти регистрацию!"),
        Next(Const("Регистрация"), id="register"),
        state=LandlordStateSG.register,
    ),
    Window(
        Const("Укажите ваше Имя:"),
        TextInput(
            id="name",
            type_factory=str,
            on_success=Next(),
            on_error=error_handler,
        ),
        Back(Const("◀️ Назад"), id="back"),
        state=LandlordStateSG.name,
    ),
    Window(
        Const("Укажите ваш контактный телефон:"),
        TextInput(
            id="phone",
            type_factory=lambda x: x if x.isdigit() else None,
            on_success=Next(),
            on_error=error_phone_handler,
        ),
        Back(Const("◀️ Назад"), id="back"),
        state=LandlordStateSG.phone,
    ),
    Window(
        Format("Подтвердите ваши данныеn\n\n Имя: <b>{name}</b>\n Телефон: <b>{phone}</b>"),
        Button(Const("✅ Подтвердить"), id="confirm", on_click=confirm_landlord_handler),
        state=LandlordStateSG.confirm,
        getter=getter_information_registration,
    ),
)


@dp.message(Command("landlord"))
async def command_landlord_process(callback: CallbackQuery, dialog_manager: DialogManager):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    check_landlord = await repo.bot_apartments.check_landlord(callback.from_user.id)
    if check_landlord:
        await dialog_manager.start(state=MenuLandlordSG.start, mode=StartMode.RESET_STACK)
    else:

        await dialog_manager.start(state=LandlordStateSG.register, mode=StartMode.RESET_STACK)