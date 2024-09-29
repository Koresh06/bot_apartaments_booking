import calendar
from operator import itemgetter
from aiogram import F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, ContentType, Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.text import Format, Const, Multi
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.common import ManagedScroll
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
    Checkbox,
    Select,
)

from src.tgbot.dialog.users.states import UserCatalogSG

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
        Start(Const("◀️ Назад"), id="back", state=UserCatalogSG.search_catalog, mode=StartMode.RESET_STACK),
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
        Back(Const("◀️ Назад")),
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
        Start(Const("Главное меню"), id="main_menu", state=UserCatalogSG.catalog, mode=StartMode.RESET_STACK),
        state=FilteredCatalogApartmentsSG.start,
        getter=getter_apartments_data,
    )
)