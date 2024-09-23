from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button, Next, Row, Back, Url, Group, SwitchTo, Start

from src.tgbot.bot import dp
from src.core.repo.requests import RequestsRepo
from src.core.config import settings

from .states import StartSG, LandlordStateSG, UserCatalogSG
from ..apartaments.states import MainSG
from .getters import start_getters, getter_information_registration
from .handlers import error_name_handler, correct_name_handler, error_phone_handler, correct_phone_handler, confirm_landlord_handler
from .utils import name_check, phone_check



start_dialog = Dialog(
    Window(
        Const("Приветствую вас в нашем сервисе по поиску квартир!"),
        Start(Const("Я ищу квартиру"), id="search", state=UserCatalogSG.catalog),
        Start(Const("Я арендодатель"), id="landlord", state=LandlordStateSG.register),
        state=StartSG.new_search,
    )
)

main_manu_dialog = Dialog(
    Window(
        Const("<b>Главное меню</b>"),
        Group(
            Start(Const("🏠 Каталог апартаментов"), id="catalog", state=MainSG.catalog, mode=StartMode.NORMAL),
            Start(Const("👤 Мой профиль"), id="profile", state=MainSG.profile, show_mode=StartMode.RESET_STACK),
            Start(Const("❓ FAQ"), id="faq", state=MainSG.faq, show_mode=StartMode.RESET_STACK),
            width=2,
        ),
        state=UserCatalogSG.catalog
    )
)

register_landlord_dialog = Dialog(
    Window(
        Const(text="Для дальнейшей работы необходимо профти регистрацию!"),
        Next(Const("Регистрация"), id="register"),
        state=LandlordStateSG.register,
    ),
    Window(
        Const("Укажите ваше Имя:"),
        TextInput(
            id="name",
            type_factory=name_check,
            on_success=correct_name_handler,
            on_error=error_name_handler,
        ),
        Back(Const("◀️ Назад"), id="back"),
        state=LandlordStateSG.name
    ),
    Window(
        Const("Укажите ваш контактный телефон:"),
        TextInput(
            id="phone",
            type_factory=phone_check,
            on_success=correct_phone_handler,
            on_error=error_phone_handler,
        ),
        Back(Const("◀️ Назад"), id="back"),
        state=LandlordStateSG.phone
    ),
    Window(
        Format("Подтвердите ваши данныеn\n\n Имя: <b>{name}</b> Телефон: <b>{phone}</b>"),
        Button(Const("✅ Подтвердить"), id="confirm", on_click=confirm_landlord_handler),
        state=LandlordStateSG.confirm,
        getter=getter_information_registration,
    )
)


@dp.message(CommandStart())
async def command_start_process(callback: CallbackQuery, dialog_manager: DialogManager):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    user = await repo.users.check_new_user(callback.from_user.id)

    if user:
        await dialog_manager.start(state=StartSG.current_start, mode=StartMode.RESET_STACK)
    else:
        await dialog_manager.start(state=StartSG.new_search, mode=StartMode.RESET_STACK)