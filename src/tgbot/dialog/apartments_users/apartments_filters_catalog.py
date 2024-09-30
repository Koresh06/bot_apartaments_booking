from operator import itemgetter
from aiogram import F
from aiogram.filters import CommandStart, Command
from aiogram.types import CallbackQuery, Message
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
    Select,
)

from src.core.repo.requests import RequestsRepo
from src.tgbot.bot import dp
from src.tgbot.dialog.apartments_landlord.getters import getter_apartment_details
from .handlers import handle_city_filter, handle_confirm_min_max_price, handle_room_filter, on_booking
from .states import FilterCitysSG, FilterPricePerDaySG, FilterRoomsSG, FiltersApartmentsSG, FilteredCatalogApartmentsSG
from .getters import getter_apartments_data, getter_get_city, getter_get_rooms, getter_min_max_price
from src.tgbot.dialog.apartments_landlord.handlers import error_handler, on_next, on_prev


filter_catalog_apartments_dialog = Dialog(
    Window(
        Const("Фильтр каталога апартаментов"),
        Group(
            Start(Const("Город"), id="city", state=FilterCitysSG.start),  
            Start(Const("Диапазон цен"), id="price_per_day", state=FilterPricePerDaySG.min_price),  
            Start(Const("Комнаты"), id="rooms", state=FilterRoomsSG.start),
            width=2,
        ),
        state=FiltersApartmentsSG.start,
    ),
)


city_filter_apartment_dialog = Dialog(
    Window(
        Const("Фильтр по городам"),
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
        Start(Const("◀️ Назад"), id="back", state=FiltersApartmentsSG.start, mode=StartMode.RESET_STACK),
        state=FilterCitysSG.start,
        getter=getter_get_city
    ),
)

price_range_filter_dialog = Dialog(
    Window(
        Const("Укажите минимальную цену:"),
        TextInput(
            id="min_price",
            type_factory=float,
            on_success=Next(),
            on_error=error_handler,
        ),
        Start(Const("◀️ Назад"), id="back", state=FiltersApartmentsSG.start, mode=StartMode.RESET_STACK),
        state=FilterPricePerDaySG.min_price,
    ),
    Window(
        Const("Укажите максимальную цену:"),
        TextInput(
            id="max_price",
            type_factory=float,
            on_success=Next(),
            on_error=error_handler,
        ),
        Back(Const("◀️ Назад")),
        state=FilterPricePerDaySG.max_price,
    ),
    Window(
        Format("Указанный диапазон цен: <b>{min_price}-{max_price}</b>"),
        Button(Const("✅ Подтвердить"), id="confirm", on_click=handle_confirm_min_max_price),
        Back(Const("◀️ Назад")),
        state=FilterPricePerDaySG.confirm,
        getter=getter_min_max_price,
    ),
)


rooms_filter_dialog = Dialog(
    Window(
        Const("Выберите количество комнат:"),
        Group(
            Select(
                Format("{item[0]}"),
                id="room",
                items="rooms",
                item_id_getter=itemgetter(1),
                on_click=handle_room_filter,
            ),
            width=4,
        ),
        Start(Const("◀️ Назад"), id="back", state=FiltersApartmentsSG.start, mode=StartMode.RESET_STACK),
        state=FilterRoomsSG.start,
        getter=getter_get_rooms,
    )
)


catalog_users_apartments_dialog = Dialog(
    Window(
        Format(
            "<b>ID: {apartment[apartment_id]}</b>\n"
            "<b>Город: {apartment[city]}</b>\n"
            "<b>Улица: {apartment[street]}</b>\n"
            "<b>Дом: {apartment[house_number]}</b>\n"
            "<b>Квартира: {apartment[apartment_number]}</b>\n"
            "<b>Цена за день: {apartment[price_per_day]}</b>\n"
            "<b>Комнат: {apartment[rooms]}</b>\n"
            "<b>Описание: {apartment[description]}</b>\n"
        ),
        DynamicMedia(selector="media"),
        Next(Const("Детали"), id="details"),
        Button(Const("Бронировать"), id="booking", on_click=on_booking),
        Row(
            Button(Const("◀️ Назад"), id="next", on_click=on_prev),
            Button(
                Format("{current_page}/{count_page}"),
                id="paginator",
            ),
            Button(Const("Вперед ▶️"), id="prev", on_click=on_next),
            when="is_apartments",
        ),
        Start(Const("Фильтры"), id="main_menu", state=FiltersApartmentsSG.start, mode=StartMode.RESET_STACK, when="check_filters"),
        state=FilteredCatalogApartmentsSG.start,
        getter=getter_apartments_data,
    ),
    Window(
        Format(
            "<b>Город: {apartment[city]}</b>\n"
            "<b>Улица: {apartment[street]}</b>\n"
            "<b>Дом: {apartment[house_number]}</b>\n"
            "<b>Квартира: {apartment[apartment_number]}</b>\n"
            "<b>Цена за день: {apartment[price_per_day]}</b>\n"
            "<b>Комнат: {apartment[rooms]}</b>\n"
            "<b>Описание: {apartment[description]}</b>\n"
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
    )
)



@dp.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    print("Start!")
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    await repo.bot_users.add_user(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
    )
    await dialog_manager.start(state=FilteredCatalogApartmentsSG.start, data={"city": None, "price_range": None, "rooms": None}, mode=StartMode.RESET_STACK)


@dp.message(Command("filter"))
async def command_filter_process(callback: CallbackQuery, dialog_manager: DialogManager):
    await dialog_manager.start(state=FiltersApartmentsSG.start, mode=StartMode.RESET_STACK)