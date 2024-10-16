from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import StartMode, Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, Start, Url, Next, Back
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput

from src.core.models.users import Users
from src.core.repo.requests import RequestsRepo
from src.tgbot.dialog.apartments_landlord.handlers import error_handler

from src.core.config import config
from .states import MainAdminSG, RegisterNameCitysSG
from .getters import getter_name_city
from .handlers import handle_register_name_city


router = Router()


main_admin_dialog = Dialog(
    Window(
        Const("🛠️ Администратор"),
        Start(Const("🌆 Добавить город"), id="add_city", state=RegisterNameCitysSG.start, show_mode=StartMode.RESET_STACK),
        Url(Const("🔗 Панель администратора"), url=Const(config.api.web_url)),
        state=MainAdminSG.start,
    )
)


register_name_city_dialog = Dialog(
    Window(
        Const("🏙️ Укажите название города:"),
        TextInput(
            id="name",
            type_factory=str,
            on_success=Next(),
            on_error=error_handler,
        ),
        Start(Const("◀️ Назад"), id="back", state=RegisterNameCitysSG.start, mode=StartMode.RESET_STACK),
        state=RegisterNameCitysSG.start,
    ),
    Window(
        Format("🌆 Название города: <b>{name}</b>"),
        Button(Const("✅ Подтвердить"), id="confirm", on_click=handle_register_name_city),
        Back(Const("◀️ Назад")),
        state=RegisterNameCitysSG.confirm,
    ),
    getter=getter_name_city,
)


@router.message(Command("admin"))
async def command_admin(message: Message, dialog_manager: DialogManager):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    user: Users = await repo.admin_bot.check_is_admin(message.from_user.id)
    if user.is_admin or user.is_superuser:
        await dialog_manager.start(state=MainAdminSG.start, mode=StartMode.RESET_STACK)
    else:
        await message.answer("Доступ запрещен")