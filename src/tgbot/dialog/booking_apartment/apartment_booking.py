from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Next,
    Back,
)

from src.core.repo.requests import RequestsRepo

from .custom_calendar import CustomCalendar
from .states import BookingApartmentSG, ConfirmBooking
from .handlers import (
    back_to_catalog_apartments,
    handle_confirm_booking,
    no_confirm_booking,
    on_end_date_selected,
    on_start_date_selected,
    yes_confirm_booking,
)
from .getters import getter_date_and_booked_dates
from .keyboard import PhoneCbData, landlord_keyboard, phone_keyboard


router = Router()


booking_apartment = Dialog(
    Window(
        Const("📅 Выберите дату начала бронирования"),
        CustomCalendar(
            id="start_calendar",
            on_click=on_start_date_selected,
        ),
        Button(Const("◀️ Назад"), id="back", on_click=back_to_catalog_apartments),
        state=BookingApartmentSG.start_date,
    ),
    Window(
        Const("📅 Выберите дату окончания бронирования"),
        Format("🗓️ Дата начала бронирования: {start_date}"),
        CustomCalendar(
            id="end_calendar",
            on_click=on_end_date_selected,
        ),
        Back(Const("◀️ Назад")),
        state=BookingApartmentSG.end_date,
    ),
    Window(
        Format(
            "📅 Дата начала бронирования: {start_date}\n📅 Дата окончания бронирования: {end_date}"
        ),
        Button(Const("✅ Подтвердить"), id="confirm", on_click=handle_confirm_booking),
        Back(Const("◀️ Назад")),
        state=BookingApartmentSG.confirm,
    ),
    getter=getter_date_and_booked_dates
)


confirm_booking_landlord_dialog = Dialog(
    Window(
        Const("📅 Подтвердите бронирование апартамента"),
        Format(
            "<b>ID: {apartment[apartment_id]}</b>\n"
            "<b>🏙️ Город: {apartment[city]}</b>\n"
            "<b>🛣️ Улица: {apartment[street]}</b>\n"
            "<b>🏠 Дом: {apartment[house_number]}</b>\n"
            "<b>🏢 Квартира: {apartment[apartment_number]}</b>\n"
            "<b>💰 Цена за день: {apartment[price_per_day]} ₽</b>\n"
            "<b>🛏️ Комнат: {apartment[rooms]}</b>\n"
            "<b>📝 Описание: {apartment[description]}</b>\n"
        ),
        Button(Const("✅ Подтвердить"), id="confirm", on_click=yes_confirm_booking),
        Next(Const("❌ Отменить")),
        state=ConfirmBooking.start,
    ),
    Window(
        Const("✏️ Укажите причину отмены бронирования:"),
        TextInput(
            id="cancel_reason",
            type_factory=str,
            on_success=Next(),
        ),
        Back(Const("◀️ Назад"), id="back"),
        state=ConfirmBooking.cancle_message,
    ),
    Window(
        Const("⚠️ Вы уверены, что хотите отменить бронирование?"),
        Button(Const("✅ Подтвердить"), id="confirm", on_click=no_confirm_booking),
        Back(Const("◀️ Назад"), id="back"),
        state=ConfirmBooking.cancle_сonfirm,
    ),
    getter=getter_date_and_booked_dates,
)


@router.callback_query(PhoneCbData.filter())
async def phone_callback(callback: CallbackQuery, callback_data: PhoneCbData, repo: RequestsRepo):
    await repo.apartment_bookings.update_clicks_phone(landlord_id=callback_data.landlord_id)
    
    await callback.message.edit_text(
        text=f"Информация об арендаторе:\n🏠 Имя: {callback_data.name}\n📞 Телефон: {callback_data.phone}\n",
        reply_markup= await phone_keyboard(tg_id=callback_data.tg_id)
    )
