from datetime import date, datetime, time
from functools import partial
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.types import CallbackQuery, User, Chat
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram_dialog.manager.bg_manager import BgManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.input import TextInput

from src.core.models.bookings import Booking
from src.core.repo.requests import RequestsRepo
from src.tgbot import dp, bot
from src.tgbot.dialog.apartments_users.states import (
    FilteredCatalogApartmentsSG,
    FiltersApartmentsSG,
    FiltersSG,
)
from .states import ConfirmBooking
from .keyboard import phone_keyboard


async def on_start_date_selected(
    callback: CallbackQuery, widget, dialog_manager: DialogManager, start_date: date
):
    today = date.today()
    
    apartment_id = dialog_manager.start_data.get("apartment")["apartment_id"]
    
    bookings = dialog_manager.dialog_data.get("bookings")
    
    booked_dates = []
    
    for booking_data in bookings:
        booking = booking_data["booking"]
        if booking.apartment_id == apartment_id:
            booked_dates.append({
                "start_date": booking.start_date.date(),
                "end_date": booking.end_date.date()      
            })
    
    for booked in booked_dates:
        if booked["start_date"] <= start_date <= booked["end_date"]:
            await callback.answer("🛑 Эта дата уже занята.", show_alert=True)
            return 
    
    if start_date < today:
        await callback.answer("🚫 Эта дата недоступна.", show_alert=True)
    else:
        dialog_manager.dialog_data["start_date"] = start_date
        await callback.answer(
            f"📅 Дата начала бронирования: {start_date}", show_alert=True
        )
        await dialog_manager.next()


async def on_end_date_selected(
    callback: CallbackQuery, widget, dialog_manager: DialogManager, end_date: date
):
    today = date.today()
    start_date = dialog_manager.dialog_data.get("start_date")

    apartment_id = dialog_manager.start_data.get("apartment")["apartment_id"]

    bookings = dialog_manager.dialog_data.get("bookings")

    booked_dates = []

    for booking_data in bookings:
        booking = booking_data["booking"]
        if booking.apartment_id == apartment_id:
            booked_dates.append({
                "start_date": booking.start_date.date(), 
                "end_date": booking.end_date.date()      
            })

    # Проверка на занятость новой конечной даты
    for booked in booked_dates:
        # Проверяем пересечения
        if (start_date and booked["start_date"] <= end_date <= booked["end_date"]) or \
           (start_date and start_date <= booked["end_date"] and end_date >= booked["start_date"]):
            await callback.answer("❌ Невозможно выбрать эти даты, так как в указанном промежутке уже есть забронированные дни.", show_alert=True)
            return  

    if end_date < today:
        await callback.answer("🚫 Эта дата недоступна.", show_alert=True)
    elif start_date and end_date <= start_date:
        await callback.answer(
            "⚠️ Дата выезда должна быть позже даты заезда.", show_alert=True
        )
    else:
        dialog_manager.dialog_data["end_date"] = end_date
        await callback.answer(
            f"📅 Дата окончания бронирования: {end_date}", show_alert=True
        )
        await dialog_manager.next()


async def back_to_catalog_apartments(
    callback: CallbackQuery, widget: Button, dialog_manager: DialogManager
):
    city_id = dialog_manager.start_data.get("city_id")
    price_range = dialog_manager.start_data.get("price_range")
    room = dialog_manager.start_data.get("room")


    await dialog_manager.start(
        state=FilteredCatalogApartmentsSG.start,
        mode=StartMode.RESET_STACK,
        data={
            "city_id": city_id,
            "price_range": price_range,
            "room": room,
        },
    )


async def handle_confirm_booking(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    start_date = dialog_manager.dialog_data.get("start_date")
    end_date = dialog_manager.dialog_data.get("end_date")

    apartment = dialog_manager.start_data.get("apartment")
    landlord_id = apartment["landlord_tg_id"]
    apartment_id = apartment["apartment_id"]
    landlord_chat_id = apartment["landlord_chat_id"]

    # Сохранение бронирования
    booking: Booking = await repo.apartment_bookings.save_booking(
        tg_id=callback.from_user.id,
        apartment_id=apartment_id,
        start_date=start_date,
        end_date=end_date,
    )
    if booking:
        await callback.answer(
            text=(
                "🎉 Поздравляем! Апартамент забронирован и сейчас обрабатывается арендодателем.\n\n"
                f"📅 Начало аренды: {str(start_date)}\n"
                f"📅 Окончание аренды: {str(end_date)}\n\n"
                "⏳ Ожидайте подтверждения. Уведомим о результате!"
            ),
            show_alert=True,
        )

        user = User(id=landlord_id, is_bot=False, first_name="landlord")
        chat = Chat(id=landlord_chat_id, type="private")
        bg_manager = BgManager(
            chat=chat, user=user, bot=bot, router=dp, intent_id=None, stack_id=""
        )
        await bg_manager.start(
            state=ConfirmBooking.start,
            data={
                "booking": booking,
                "apartment": apartment,
                "user_id": callback.from_user.id,
            },
            show_mode=ShowMode.SEND,
        )

        await dialog_manager.start(
            state=FiltersSG.city,
            mode=StartMode.RESET_STACK,
        )
    else:
        await callback.answer(text="Что-то пошло не так, попробуйте еще раз")


async def yes_confirm_booking(
    callback: CallbackQuery, widget: Button, dialog_manager: DialogManager
):
    booking: Booking = dialog_manager.start_data.get("booking")
    user_id = dialog_manager.start_data.get("user_id")
    apartment_id = dialog_manager.start_data.get("apartment")["apartment_id"]
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get("scheduler")

    confirm = await repo.apartment_bookings.booking_is_confirmation(
        booking_id=booking.id
    )

    if confirm:
        # landlord = await repo.booking_api.get_landlord_by_apartment(apartment_id=apartment_id)
        await bot.send_message(
            chat_id=user_id, text="Поздравляем! ✅ Бронирование успешно подтверждено!", reply_markup= await phone_keyboard(tg_id=user_id)   
        )

        # Устанавливаем время начало бронирования + сокрытие апартамента из каталога. start_date (дата начала бронирования)
        start_time = datetime.date(booking.start_date)
        # start_time = datetime.now() + timedelta(seconds=15) # Тестовое время начала бронирования
        func_apartment = partial(
            repo.apartment_bookings.installation_false_is_available_apartment,
            apartment_id,
        )
        scheduler.add_job(func=func_apartment, trigger="date", run_date=start_time)

        # Устанавливаем время завершения бронирования end_date (дата окончания бронирования) - 12:00 (по Бишкекскому времени) + зменение статуса на завершонную бронь
        end_time = datetime.combine(booking.end_date, time(9, 0))
        # end_time = datetime.now() + timedelta(seconds=30) # Тестовое время окончания бронирования
        func_booking = partial(
            repo.apartment_bookings.update_is_completed_booking, booking.id
        )
        scheduler.add_job(func=func_booking, trigger="date", run_date=end_time)

        await dialog_manager.done(show_mode=ShowMode.DELETE_AND_SEND)
    else:
        await callback.answer(
            text="Не удалось подтвердить бронирование. Попробуйте еще раз."
        )


async def no_confirm_booking(
    callback: CallbackQuery, widget: Button, dialog_manager: DialogManager
):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    booking: Booking = dialog_manager.start_data.get("booking")
    user_id = dialog_manager.start_data.get("user_id")
    message: TextInput = dialog_manager.find("cancel_reason").get_value()
    del_bookint = await repo.apartment_bookings.delete_booking(booking_id=booking.id)
    if del_bookint:
        await bot.send_message(
            chat_id=user_id,
            text=f"⚠️ К сожалению, ваше бронирование отменено. \n\n📖 Причина: <b>{message}</b>",
        )
        await callback.answer(text="Бронирование отменено.")
        await dialog_manager.done(show_mode=ShowMode.DELETE_AND_SEND)
    else:
        await callback.answer(
            text="Не удалось отменить бронирование. Попробуйте еще раз."
        )
