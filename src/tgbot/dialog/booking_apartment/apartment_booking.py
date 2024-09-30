from aiogram_dialog import Dialog, StartMode, Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Next,
    Back,
    Start
)

from src.tgbot.dialog.apartments_users.states import FilteredCatalogApartmentsSG


from .custom_calendar import CustomCalendar
from .states import BookingApartmentSG, ConfirmBooking
from .handlers import back_to_catalog_apartments, handle_confirm_booking, no_confirm_booking, on_end_date_selected, on_start_date_selected, yes_confirm_booking
from .getters import getter_confirm_landlord_booking, getter_date



booking_apartment = Dialog(
    Window(
        Const("Выберите дату начала аренды"),
        CustomCalendar(
            id="start_calendar",
            on_click=on_start_date_selected,
        ),
        Button(Const("◀️ Назад"), id="back", on_click=back_to_catalog_apartments),
        state=BookingApartmentSG.start_date,
    ),
    Window(
        Const("Выберите дату окончания аренды"),
        Format("Дата окончания аренды: {start_date}"),
        CustomCalendar(
            id="end_calendar",
            on_click=on_end_date_selected,
        ),
        Back(Const("◀️ Назад")),
        state=BookingApartmentSG.end_date,
    ),
    Window(
        Format("Дата начала аренды: {start_date}\nДата окончания аренды: {end_date}"),
        Button(Const("✅ Подтвердить"), id="confirm", on_click=handle_confirm_booking),
        Back(Const("◀️ Назад")),
        state=BookingApartmentSG.confirm,
    ),
    getter=getter_date,
)


confirm_booking_landlord_dialog = Dialog(
    Window(
        Const("Подтвердите бронирование апартамента"),
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
        Button(Const("✅ Подтвердить"), id="confirm", on_click=yes_confirm_booking),
        Next(Const("❌ Отменить")),
        state=ConfirmBooking.start,
    ),
    Window(
        Const("Укажите причину отмены бронирования:"),
        TextInput(
            id="cancel_reason",
            type_factory=str,
            on_success=Next(),
        ),
        Back(Const("◀️ Назад"), id="back"),
        state=ConfirmBooking.cancle_message,
    ),
    Window(
        Const("Убедитесь, что вы уверены, что хотите отменить бронирование"),
        Button(Const("✅ Подтвердить"), id="confirm", on_click=no_confirm_booking),
        Back(Const("◀️ Назад"), id="back"),
        state=ConfirmBooking.cancle_сonfirm,
    ),
    getter=getter_confirm_landlord_booking,
)