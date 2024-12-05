from operator import itemgetter
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ContentType
from aiogram_dialog import StartMode, Dialog, Window, DialogManager
from aiogram_dialog.widgets.text import Format, Const, Multi
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Next,
    Row,
    Back,
    Group,
    SwitchTo,
    Start,
    NumberedPager,
    StubScroll,
    Select,
    Url
)

from src.core.models.users import Users
from src.core.repo.requests import RequestsRepo
from src.tgbot.dialog.apartments_landlord.getters import getter_get_city, getter_get_media
from src.tgbot.dialog.apartments_landlord.handlers import error_handler, handle_city, on_delete, on_input_photo, skip_apartment_number_handler

from src.core.config import config
from src.tgbot.dialog.apartments_landlord.states import MenuLandlordSG
from .states import MainAdminSG, RegisterNameCitysSG, RegisterApartmentLandlordSG
from .getters import getter_landlords, getter_name_city
from .handlers import admin_confirm_deteils_apartment_landlord, handle_register_apartament_by_landlord, handle_register_name_city


router = Router()


main_admin_dialog = Dialog(
    Window(
        Const("🛠️ Администратор"),
        Start(Const("🌆 Добавить город"), id="add_city", state=RegisterNameCitysSG.start, show_mode=StartMode.RESET_STACK),
        Start(Const("🏙️ Добавить апартамент"), id="add_apartment_landlord", state=RegisterApartmentLandlordSG.landlord, show_mode=StartMode.RESET_STACK),
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
        Start(Const("◀️ Назад"), id="back", state=MainAdminSG.start, mode=StartMode.RESET_STACK),
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


register_apartament_by_landlord_dialog = Dialog(
    Window(
        Const("🏠 Выберите арендодателя:"),
        Group(
            Select(
                Format("{item[1]}"),
                id="landlord",
                items="landlords",
                item_id_getter=itemgetter(0),
                on_click=handle_register_apartament_by_landlord,
            )
        ),
        Start(Const("◀️ Назад"), id="back", state=MainAdminSG.start, mode=StartMode.RESET_STACK),
        getter=getter_landlords,
        state=RegisterApartmentLandlordSG.landlord,
    ),
    Window(
        Const("🏙️ Выберите город:"),
        Group(
            Select(
                Format("🌆 {item[1]}"),
                id="city",
                items="citys",
                item_id_getter=itemgetter(0),
                on_click=handle_city,
            ),
            width=4,
        ),
        Row(
            Start(
                Const("◀️ Назад"),
                id="cancel_form_register",
                state=MenuLandlordSG.start,
                show_mode=StartMode.RESET_STACK,
            ),
        ),
        state=RegisterApartmentLandlordSG.city,
        getter=getter_get_city,
    ),
    Window(
        Multi(
            Const("🏠 Отправьте название улицы:"),
            Format("🛣️ Название улицы: {street}", when="street"),
            sep="\n\n",
        ),
        TextInput(
            id="street",
            type_factory=str,
            on_success=Next(),
            on_error=error_handler,
        ),
        Row(
            Back(Const("⬅️ Назад")),
            Next(when="street"),
        ),
        state=RegisterApartmentLandlordSG.street,
    ),
    Window(
        Multi(
            Const("🏡 Отправьте номер дома:"),
            Format("🏠 Номер дома: {house_number}", when="house_number"),
            sep="\n\n",
        ),
        TextInput(
            id="house_number",
            type_factory=int,
            on_success=Next(),
            on_error=error_handler,
        ),
        Row(
            Back(Const("⬅️ Назад")),
            Next(when="house_number"),
        ),
        state=RegisterApartmentLandlordSG.house_number,
    ),
    Window(
        Multi(
            Const("🏢 Отправьте номер квартиры (если необходимо!):"),
            Format("🏡 Номер квартиры: {apartment_number}", when="apartment_number"),
            sep="\n\n",
        ),
        TextInput(
            id="apartment_number",
            type_factory=int,
            on_success=Next(),
            on_error=error_handler,
        ),
        Button(
            Const("🔄 Пропустить"), id="skip", on_click=skip_apartment_number_handler
        ),
        Back(Const("◀️ Назад")),
        Next(when="apartment_number"),
        state=RegisterApartmentLandlordSG.apartment_number,
    ),
    Window(
        Multi(
            Const("💰 Отправьте цену за день:"),
            Format("💵 Цена за день: {price_per_day}", when="price_per_day"),
            sep="\n\n",
        ),
        TextInput(
            id="price_per_day",
            type_factory=float,
            on_success=Next(),
            on_error=error_handler,
        ),
        Row(
            Back(Const("⬅️ Назад")),
            Next(when="price_per_day"),
        ),
        state=RegisterApartmentLandlordSG.price_per_day,
    ),
    Window(
        Multi(
            Const("🛏️ Отправьте количество комнат:"),
            Format("🛌 Количество комнат: {rooms}", when="rooms"),
            sep="\n\n",
        ),
        TextInput(
            id="rooms",
            type_factory=int,
            on_success=Next(),
            on_error=error_handler,
        ),
        Row(
            Back(Const("⬅️ Назад")),
            Next(when="rooms"),
        ),
        state=RegisterApartmentLandlordSG.rooms,
    ),
    Window(
        Multi(
            Const("📝 Отправьте описание вашего апартамента:"),
            Format("📖 Описание: {description}", when="description"),
            sep="\n\n",
        ),
        TextInput(
            id="description",
            type_factory=str,
            on_success=Next(),
            on_error=error_handler,
        ),
        Row(
            Back(Const("⬅️ Назад")),
            Next(when="description"),
        ),
        state=RegisterApartmentLandlordSG.description,
    ),
    Window(
        Const("📸 Отправьте фото вашего апартамента (можно сразу группой фото)"),
        DynamicMedia(selector="media"),
        StubScroll(id="pages", pages="media_count"),
        Group(
            NumberedPager(scroll="pages", when=F["pages"] > 1),
            width=8,
        ),
        Button(
            Format("🗑️ Удалить фото #{media_number}"),
            id="del",
            on_click=on_delete,
            when="media_count",
        ),
        MessageInput(content_types=[ContentType.PHOTO], func=on_input_photo),
        Next(Const("➡️ Далее"), id="confirm_photos", when="confirm"),
        Back(Const("◀️ Назад")),
        state=RegisterApartmentLandlordSG.photo,
        getter=getter_get_media,
    ),
    Window(
        Format(
            "<b>🏙️ Город: {city}</b>\n"
            "<b>🛣️ Улица: {street}</b>\n"
            "<b>🏠 Дом: {house_number}</b>\n"
            "<b>🏢 Квартира: {apartment_number}</b>\n"
            "<b>💵 Цена за день: {price_per_day}</b>\n"
            "<b>🛌 Комнат: {rooms}</b>\n"
            "<b>📖 Описание: {description}</b>\n"
        ),
        DynamicMedia(selector="media"),
        StubScroll(id="pages", pages="media_count"),
        Group(
            NumberedPager(scroll="pages", when=F["pages"] > 1),
            width=8,
        ),
        Button(Const("✅ Подтвердить"), id="confirm", on_click=admin_confirm_deteils_apartment_landlord),
        Start(
            Const("❌ Отмена"),
            id="cancel_form_register",
            state=MainAdminSG.start,
            show_mode=StartMode.RESET_STACK,
        ),
        state=RegisterApartmentLandlordSG.confirm,
        getter=getter_get_media,
    ),
    
)


@router.message(Command("admin"))
async def command_admin(message: Message, dialog_manager: DialogManager):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    user: Users = await repo.admin_bot.check_is_admin(message.from_user.id)
    if user.is_admin or user.is_superuser:
        await dialog_manager.start(state=MainAdminSG.start, mode=StartMode.RESET_STACK)
    else:
        await message.answer("Доступ запрещен")