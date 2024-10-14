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
from src.tgbot.dialog.apartments_users.states import FilteredCatalogApartmentsSG
from .states import ConfirmBooking


async def on_start_date_selected(callback: CallbackQuery, widget, dialog_manager: DialogManager, start_date: date):
    today = date.today()  # Получаем сегодняшнюю дату
    
    if start_date < today:
        await callback.answer("Эта дата недоступна. Пожалуйста, выберите сегодняшнюю или будущую дату.")
    else:
        dialog_manager.dialog_data["start_date"] = start_date
        await callback.answer(f"Дата начала аренды: {start_date}", show_alert=True)  # Отправляем выбранную дату
        await dialog_manager.next()


async def on_end_date_selected(callback: CallbackQuery, widget, dialog_manager: DialogManager, end_date: date):
    start_date = dialog_manager.dialog_data.get("start_date")

    if start_date and end_date <= start_date:
        await callback.answer("Дата выезда должна быть позже даты заезда.", show_alert=True)
    else:
        dialog_manager.dialog_data["end_date"] = end_date
        await callback.answer(f"Дата окончания аренды: {end_date}", show_alert=True)  # Отправляем выбранную дату
        await dialog_manager.next()


async def back_to_catalog_apartments(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    apartment = dialog_manager.start_data.get("apartment")
    await dialog_manager.start(state=FilteredCatalogApartmentsSG.start, mode=StartMode.RESET_STACK, data=apartment)


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
        await callback.answer(text="Поздравляем! ✅ Апартамент забронирован!\n\nДата начала аренды: " + str(start_date) + "\nДата окончания аренды: " + str(end_date))

        user = User(id=landlord_id, is_bot=False, first_name="landlord")
        chat = Chat(id=landlord_chat_id, type="private")
        bg_manager = BgManager(chat=chat, user=user, bot=bot, router=dp, intent_id=None, stack_id="")
        await bg_manager.start(state=ConfirmBooking.start, data={"booking": booking, "apartment": apartment, "user_id": callback.from_user.id}, show_mode=ShowMode.SEND)
        
        await dialog_manager.start(state=FilteredCatalogApartmentsSG.start, data={"city": None, "price_range": None, "rooms": None}, mode=StartMode.RESET_STACK)
    else:
        await callback.answer(text="Что-то пошло не так, попробуйте еще раз")



async def yes_confirm_booking(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    booking: Booking = dialog_manager.start_data.get("booking")
    user_id = dialog_manager.start_data.get("user_id")
    apartment_id = dialog_manager.start_data.get("apartment")["apartment_id"]
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get("scheduler")
    
    confirm = await repo.apartment_bookings.booking_confirmation(booking_id=booking.id, apartment_id=apartment_id)
    
    if confirm:
        await bot.send_message(chat_id=user_id, text="Поздравляем! ✅ Бронирование успешно подтверждено!")
        
        # Устанавливаем время окончания на 12:00
        update_time = datetime.combine(booking.end_date, time(9, 0)) # Устанавливаем время через 1 день в 12:00 (по Бишкекскому времени)
        # update_time = datetime.now() + timedelta(seconds=10)
        # Запускаем задачу для обновления статуса бронирования
        func = partial(repo.apartment_bookings.update_booking_status, booking.id)
        scheduler.add_job(func=func, trigger='date', run_date=update_time)
        
        await dialog_manager.done(show_mode=ShowMode.DELETE_AND_SEND)
    else:
        await callback.answer(text="Не удалось подтвердить бронирование. Попробуйте еще раз.")


async def no_confirm_booking(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    booking: Booking = dialog_manager.start_data.get("booking")
    user_id = dialog_manager.start_data.get("user_id")
    message: TextInput = dialog_manager.find("cancel_reason").get_value()
    del_bookint = await repo.apartment_bookings.delete_booking(booking_id=booking.id)
    if del_bookint:
        await bot.send_message(chat_id=user_id, text=f"⚠️ К сожалению, ваше бронирование отменено. \n\n📖 Причина: <b>{message}</b>")
        await callback.answer(text="Бронирование отменено.")
        await dialog_manager.done(show_mode=ShowMode.DELETE_AND_SEND)
    else:
        await callback.answer(text="Не удалось отменить бронирование. Попробуйте еще раз.")


