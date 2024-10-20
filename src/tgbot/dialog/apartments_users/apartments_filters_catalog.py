from operator import itemgetter
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Next,
    Row,
    Back,
    Group,
    Start,
    NumberedPager,
    StubScroll,
    Select
)

from src.core.repo.requests import RequestsRepo
from src.tgbot.dialog.apartments_landlord.getters import getter_apartment_details
from .handlers import (
    handle_city_filter,
    handle_confirm_min_max_price,
    handle_room_filter,
    on_booking,
    on_phone,
)
from .states import (
    FilteredCatalogApartmentsSG,
    FiltersSG
)
from .getters import (
    getter_apartments_data,
    getter_filters,
    getter_get_city,
    getter_get_rooms,
    getter_min_max_price,
)
from src.tgbot.dialog.apartments_landlord.handlers import error_handler, on_next, on_prev


router = Router()


filter_catalog_apartments_dialog = Dialog(
    Window(
        Const("🌆 Выберите город"),
        Group(
            Select(
                Format("{item[0]}"),
                id="city",
                items="citys",
                item_id_getter=itemgetter(1),
                on_click=handle_city_filter,
            ),
            width=4,
        ),
        state=FiltersSG.city,
        getter=getter_get_city,
    ),
    Window(
        Const("⚠️ Внимание! На данный момент информация по данному городу отсутствует. Попробуйте позже. Нажмите - /start", when=~F["count"]),
        Const("💰 Укажите минимальную цену:", when="count"),
        TextInput(
            id="min_price",
            type_factory=float,
            on_success=Next(),
            on_error=error_handler,
        ),
        Back(Const("◀️ Назад"), when="count"),
        state=FiltersSG.min_price,
    ),
    Window(
        Const("💸 Укажите максимальную цену:"),
        TextInput(
            id="max_price",
            type_factory=float,
            on_success=Next(),
            on_error=error_handler,
        ),
        Back(Const("◀️ Назад")),
        state=FiltersSG.max_price,
    ),
    Window(
        Format("📊 Указанный диапазон цен: <b>{min_price}-{max_price}</b>"),
        Button(
            Const("✅ Подтвердить"), id="confirm", on_click=handle_confirm_min_max_price
        ),
        Back(Const("◀️ Назад")),
        state=FiltersSG.confirm_range,
        getter=getter_min_max_price,
    ),
    Window(
        Const("⚠️ Внимание! На данный момент информация по данному диапазону цен отсутствует. Попробуйте позже.\nВернитесь назад и укажите новый диапазон или нажмите - /start", when=~F["count"]),
        Const("🏠 Выберите количество комнат:", when="count"),
        Group(
            Select(
                Format("{item[0]}"),
                id="room",
                items="rooms",
                item_id_getter=itemgetter(1),
                on_click=handle_room_filter,
            ),
            width=4,
            when="count"
        ),
        Back(Const("◀️ Назад")),
        state=FiltersSG.rooms,
        getter=getter_get_rooms,
    ),
    getter=getter_filters,
)


catalog_users_apartments_dialog = Dialog(
    Window(
        Const(
            "⚠️ На данный момент нет доступных апартаментов. "
            "Попробуйте изменить фильтры поиска 🔍 или загляните позже 🕒. "
            "Мы постоянно обновляем информацию! 🔄",
            when=~F["data"],
        ),
        Format(
            "<b>🌆 Город: {apartment[city]}</b>\n"
            "<b>🛣️ Улица: {apartment[street]}</b>\n"
            "<b>🏠 Дом: {apartment[house_number]}</b>\n"
            "<b>🏢 Квартира: {apartment[apartment_number]}</b>\n"
            "<b>💰 Цена за день: {apartment[price_per_day]}₽</b>\n"
            "<b>🛏️ Количество комнат: {apartment[rooms]}</b>\n"
            "<b>📝 Описание: {apartment[description]}</b>\n",
            when="data",
        ),
        DynamicMedia(selector="media", when="data"),
        Group(
            Next(Const("🔍 Детали"), id="details"),
            Button(Const("📞 Телефон"), id="phone", on_click=on_phone),
            Button(Const("📅 Бронировать"), id="booking", on_click=on_booking),
            Row(
                Button(Const("◀️ Назад"), id="next", on_click=on_prev),
                Button(
                    Format("{current_page}/{count_page}"),
                    id="paginator",
                ),
                Button(Const("Вперед ▶️"), id="prev", on_click=on_next),
                when="is_apartments",
            ),
            Start(
                Const("🔍 Фильтр"),
                id="main_filters",
                state=FiltersSG.city,
                mode=StartMode.RESET_STACK,
            ),
            when="data",
        ),
        state=FilteredCatalogApartmentsSG.start,
        getter=getter_apartments_data,
    ),
    Window(
        Format(
            "<b>🌆 Город: {apartment[city]}</b>\n"
            "<b>🛣️ Улица: {apartment[street]}</b>\n"
            "<b>🏠 Дом: {apartment[house_number]}</b>\n"
            "<b>🏢 Квартира: {apartment[apartment_number]}</b>\n"
            "<b>💰 Цена за день: {apartment[price_per_day]}₽</b>\n"
            "<b>🛏️ Количество комнат: {apartment[rooms]}</b>\n"
            "<b>📝 Описание: {apartment[description]}</b>\n"
        ),
        DynamicMedia(selector="media"),
        StubScroll(id="pages", pages="media_count"),
        Group(
            NumberedPager(scroll="pages", when=F["pages"] > 1),
            width=8,
        ),
        Back(Const("◀️ Назад"), id="back", show_mode=StartMode.RESET_STACK),
        state=FilteredCatalogApartmentsSG.details,
        getter=getter_apartment_details,
    ),
)


@router.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    await repo.bot_users.add_user(
        tg_id=message.from_user.id,
        chat_id=message.chat.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        full_name=message.from_user.full_name,
    )
    await dialog_manager.start(state=FiltersSG.city,mode=StartMode.RESET_STACK,)


# @router.message(CommandStart())
# async def cmd_start(message: Message):
#     await message.answer("Привет!")


# @dp.message(Command("filter"))
# async def command_filter_process(
#     callback: CallbackQuery, dialog_manager: DialogManager
# ):
#     await dialog_manager.start(
#         state=FiltersApartmentsSG.start, mode=StartMode.RESET_STACK
#     )
