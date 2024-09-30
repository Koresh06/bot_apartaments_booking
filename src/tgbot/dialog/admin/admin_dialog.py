from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import StartMode, Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, Start, Url, Next, Back
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput

from src.tgbot.dialog.apartments_landlord.handlers import error_handler

from src.core.config import settings
from src.tgbot.bot import dp
from .states import MainAdminSG, RegisterNameCitysSG
from .getters import getter_name_city
from .handlers import handle_register_name_city


main_admin_dialog = Dialog(
    Window(
        Const("Администратор"),
        Start(Const("Добавить город"), id="add_city", state=RegisterNameCitysSG.start, show_mode=StartMode.RESET_STACK),
        Url(Const("Панель администратора"), url=Const(settings.api.web_server_admin)),
        state=MainAdminSG.start
    )
)

register_name_city_dialog = Dialog(
    Window(
        Const("Укажите название города:"),
        TextInput(
            id="name",
            type_factory=str,
            on_success=Next(),
            on_error=error_handler,
        ),
        Start(Const("◀️ Назад"), id="back", state=RegisterNameCitysSG.start, mode=StartMode.RESET_STACK),
        state=RegisterNameCitysSG.start
    ),
    Window(
        Format("Название города: <b>{name}</b>"),
        Button(Const("✅ Подтвердить"), id="confirm", on_click=handle_register_name_city),
        Back(Const("◀️ Назад")),
        state=RegisterNameCitysSG.confirm,
    ),
    getter=getter_name_city
)


@dp.message(Command("admin"))
async def command_admin(message: Message, dialog_manager: DialogManager):
    if message.from_user.id == settings.bot.admin_id:
        await dialog_manager.start(state=MainAdminSG.start, mode=StartMode.RESET_STACK)
    else:
        await message.answer("Доступ запрещен")