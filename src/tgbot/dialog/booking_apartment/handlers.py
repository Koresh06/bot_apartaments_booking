from datetime import date
from aiogram import Bot
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button

from src.core.models.bookings import Booking
from src.core.repo.requests import RequestsRepo
from src.tgbot.dialog.apartments_users.states import FilteredCatalogApartmentsSG
from src.tgbot.dialog.bg_manager_factory import MyBgManagerFactory
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


async def handle_confirm_booking(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    bg_manager: MyBgManagerFactory = dialog_manager.middleware_data.get("bg_manager")
    bot: Bot = dialog_manager.middleware_data.get("bot")
    start_date = dialog_manager.dialog_data.get("start_date")
    end_date = dialog_manager.dialog_data.get("end_date")

    apartment = dialog_manager.start_data.get("apartment")
    landlord_id = apartment["landlord_tg_id"]
    apartment_id = apartment["apartment_id"]
    
    # Сохранение бронирования
    booking: Booking = await repo.apartment_bookings.save_booking(
        tg_id=callback.from_user.id,
        apartment_id=apartment_id,
        start_date=start_date,
        end_date=end_date,
    )
    if booking:
        await callback.answer(text="Поздравляем! ✅ Апартамент забронирован!\n\nДата начала аренды: " + str(start_date) + "\nДата окончания аренды: " + str(end_date))
        
        # Запуск диалога для арендодателя
        dialog_manager_landlord = await bg_manager.bg(
            bot=bot,
            user_id=landlord_id,
            chat_id=callback.message.chat.id,
            load=True  # Если нужно загрузить состояние чата и пользователя
        )
        
        await dialog_manager.start(state=FilteredCatalogApartmentsSG.start, mode=StartMode.RESET_STACK)
        # Запуск диалога для подтверждения бронирования у арендодателя
        await dialog_manager_landlord.start(
            state=ConfirmBooking.start,
            data={"booking_id": booking.id, "apartment": apartment, "user_id": callback.from_user.id},
            mode=StartMode.NORMAL
        )
    else:
        await callback.answer(text="Что-то пошло не так, попробуйте еще раз")



async def yes_confirm_booking(callback: CallbackQuery, dialog_manager: DialogManager, bot: Bot):
    booking_id = dialog_manager.start_data.get("booking_id")
    user_id = dialog_manager.start_data.get("user_id")
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    confirm = await repo.apartment_bookings.booking_confirmation(booking_id=booking_id)
    if confirm:
        await bot.send_message(chat_id=user_id, text="Поздравляем! ✅ Бронирование успешно подтверждено!")
        await dialog_manager.start(state=FilteredCatalogApartmentsSG.start, mode=StartMode.RESET_STACK)
    else:
        await callback.answer(text="Не удалось подтвердить бронирование. Попробуйте еще раз.")


async def no_confirm_booking(callback: CallbackQuery, dialog_manager: DialogManager, bot: Bot):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    booking_id = dialog_manager.start_data.get("booking_id")
    del_bookint = await repo.apartment_bookings.delete_booking(booking_id=booking_id, landlord_id=callback.from_user.id)
    if del_bookint:
        await callback.answer(text="Бронирование отменено.")
        await dialog_manager.start(state=FilteredCatalogApartmentsSG.start, mode=StartMode.RESET_STACK)
    else:
        await callback.answer(text="Не удалось отменить бронирование. Попробуйте еще раз.")


