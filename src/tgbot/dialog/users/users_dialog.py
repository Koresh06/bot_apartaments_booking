from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Next,
    Row,
    Back,
    Url,
    Group,
    SwitchTo,
    Start,
)

from src.tgbot.bot import dp
from src.core.repo.requests import RequestsRepo
from src.core.config import settings

from .states import StartSG, LandlordStateSG, UserCatalogSG
from ..apartments.states import MainSG
from .getters import start_getters, getter_information_registration
from .handlers import (
    error_name_handler,
    correct_name_handler,
    error_phone_handler,
    correct_phone_handler,
    confirm_landlord_handler,
)
from .utils import name_check, phone_check
from ..apartments.states import MenuLandlordSG


start_dialog = Dialog(
    Window(
        Const("Приветствую вас в нашем сервисе по поиску квартир!"),
        Start(Const("Я ищу квартиру"), id="search", state=UserCatalogSG.catalog),
        Start(Const("😎 Я арендодатель"), id="id_landlord", state=MenuLandlordSG.start, when="landlord",),
        Start(Const("Я арендодатель"), id="id_not_landlord", state=LandlordStateSG.register, when="not_landlord"),
        state=StartSG.search,
        getter=start_getters,
    ),
)

main_manu_dialog = Dialog(
    Window(
        Const("<b>Главное меню</b>"),
        Group(
            Start(
                Const("🏠 Каталог апартаментов"),
                id="catalog",
                state=MainSG.catalog,
                mode=StartMode.NORMAL,
            ),
            Start(
                Const("👤 Мой профиль"),
                id="profile",
                state=MainSG.profile,
                show_mode=StartMode.RESET_STACK,
            ),
            Start(
                Const("❓ FAQ"),
                id="faq",
                state=MainSG.faq,
                show_mode=StartMode.RESET_STACK,
            ),
            width=2,
        ),
        state=UserCatalogSG.catalog,
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
        state=LandlordStateSG.name,
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
        state=LandlordStateSG.phone,
    ),
    Window(Format("Подтвердите ваши данныеn\n\n Имя: <b>{name}</b>\n Телефон: <b>{phone}</b>"),
        Button(Const("✅ Подтвердить"), id="confirm", on_click=confirm_landlord_handler),
        state=LandlordStateSG.confirm,
        getter=getter_information_registration,
    ),
)


@dp.message(CommandStart())
async def command_start_process(callback: CallbackQuery, dialog_manager: DialogManager):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    await repo.bot_users.add_user(
        tg_id=callback.from_user.id,
        username=callback.from_user.username,
        full_name=callback.from_user.full_name,
    )
    check_landlord = await repo.bot_apartments.check_landlord(callback.from_user.id)

    await dialog_manager.start(state=StartSG.search, mode=StartMode.RESET_STACK)
