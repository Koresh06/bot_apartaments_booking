from datetime import datetime, time
from functools import partial
from aiogram.types import CallbackQuery, Message
from aiogram.enums.parse_mode import ParseMode
from aiogram_dialog import DialogManager, StartMode, ShowMode
from aiogram_dialog.widgets.common import ManagedScroll
from aiogram_dialog.widgets.input import MessageInput, ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Button
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.core.models.bookings import Booking
from src.core.repo.requests import RequestsRepo
from src.tgbot import bot
from src.tgbot.dialog.apartments_landlord.states import MenuLandlordSG, EditApartmentSG


async def error_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
):
    await message.answer(
        text="Вы ввели некоректные данные, убедитесь, что вы правильно ввели необходимые данные"
    )


async def error_phone_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    error: ValueError,
):
    await message.answer(text="Вы ввели некорректный телефон. Попробуйте еще раз")


async def correct_name_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
) -> None:
    await message.answer("Ваше имя: " + text)
    await dialog_manager.next()


async def handle_city(
    callback: CallbackQuery, 
    widget: Button, 
    dialog_manager: DialogManager, 
    item_id: str
):
    list_citys = dialog_manager.dialog_data.get("citys")
    city_id = list_citys[len(list_citys) - 1][1]  
    dialog_manager.dialog_data["city"] = city_id
    await dialog_manager.next()
    


async def confirm_landlord_handler(
    callback: CallbackQuery,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
) -> None:
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    
    name: TextInput = dialog_manager.find("name").get_value()
    phone: TextInput = dialog_manager.find("phone").get_value()

    await repo.bot_users.add_handler(
        tg_id=callback.from_user.id,
        company_name=name,
        phone=phone,
    )

    await callback.answer(text="Поздравляем! ✅ Регисрация прошла успешно!")
    await dialog_manager.start(state=MenuLandlordSG.start, mode=StartMode.RESET_STACK)


async def skip_apartment_number_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
):
    dialog_manager.dialog_data["apartment_number"] = None
    await dialog_manager.next()


async def on_input_photo(
    message: Message,
    widget: MessageInput,
    dialog_manager: DialogManager,
):
    dialog_manager.dialog_data.setdefault("photos", []).append(
        (message.photo[-1].file_id, message.photo[-1].file_unique_id),
    )


async def on_delete(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    scroll: ManagedScroll = dialog_manager.find("pages")
    media_number = await scroll.get_page()
    photos = dialog_manager.dialog_data.get("photos", [])
    del photos[media_number]
    if media_number > 0:
        await scroll.set_page(media_number - 1)


async def confirm_photos(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    data = {
        "city_id": dialog_manager.dialog_data["city"],
        "street": dialog_manager.find("street").get_value(),
        "house_number": dialog_manager.find("house_number").get_value(),
        "apartment_number": dialog_manager.find("apartment_number").get_value(),
        "price_per_day": dialog_manager.find("price_per_day").get_value(),
        "rooms": dialog_manager.find("rooms").get_value(),
        "description": dialog_manager.find("description").get_value(),
        "photos": dialog_manager.dialog_data.get("photos", []),
    }

    if await repo.bot_apartments.register_apartment_landlord(
        tg_id=callback.from_user.id, data=data
    ):
        await callback.answer(text="Поздравляем! ✅ Апартамент зарегистрирован!")
        await dialog_manager.done()
    else:
        await callback.answer(text="Что-то пошло не так, попробуйте еще раз")


async def on_delete_apartment(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    apartment = dialog_manager.dialog_data.get("apartment")
    if await repo.bot_apartments.delete_apartment_landlord(tg_id=callback.from_user.id, apartment_id=apartment["apartment_id"]):
        await callback.answer(text="Поздравляем! ✅ Апартамент удален!")
    else:
        await callback.answer(text="Что-то пошло не так, попробуйте еще раз")


async def on_next(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    current_page = dialog_manager.dialog_data.get("page", 1)
    count_page = dialog_manager.dialog_data.get("count_page", 1)

    if current_page < count_page:
        dialog_manager.dialog_data["page"] = current_page + 1
    else:
        dialog_manager.dialog_data["page"] = 1


async def on_prev(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    current_page = dialog_manager.dialog_data.get("page", 1)
    count_page = dialog_manager.dialog_data.get("count_page", 1)

    if current_page > 1:
        dialog_manager.dialog_data["page"] = current_page - 1
    else:
        dialog_manager.dialog_data["page"] = count_page


async def handle_edit_city(
    callback: CallbackQuery, 
    widget: Button, 
    dialog_manager: DialogManager, 
    item_id: int
):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    apartment = dialog_manager.start_data
    apartment_id = apartment["apartment_id"]
    list_citys = dialog_manager.dialog_data.get("citys")
    
    city_id = int(item_id)
    city_tuple = next((city for city in list_citys if city[1] == city_id), None)
    
    city_name = city_tuple[0]
    updated = await repo.bot_apartments.update_apartment_info(
        tg_id=callback.from_user.id,
        apartment_id=apartment_id,
        widget_id=widget.widget_id,
        text=city_id
    )

    if not updated:
        await callback.message.answer("Не удалось обновить информацию. Убедитесь, что вы являетесь владельцем квартиры и все данные верны.", parse_mode=ParseMode.HTML)
    else:
        await callback.message.answer(f"Успешно изменено на: <b>{city_name}</b>", parse_mode=ParseMode.HTML)

    await dialog_manager.switch_to(state=EditApartmentSG.edit)




async def edit_data(
    callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, **_kwargs
):
    apartment = dialog_manager.dialog_data.get("apartment")
    await dialog_manager.start(
        state=EditApartmentSG.edit, mode=StartMode.NORMAL, data=apartment
    )


async def update_apartment_information(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    apartment = dialog_manager.start_data
    apartment_id = apartment["apartment_id"]

    # Вызов функции для обновления информации
    updated = await repo.bot_apartments.update_apartment_info(
        tg_id=message.from_user.id,
        apartment_id=apartment_id,
        widget_id=widget.widget.widget_id,
        text=text
    )

    if not updated:
        await message.answer("Не удалось обновить информацию. Убедитесь, что вы являетесь владельцем квартиры и все данные верны.", parse_mode=ParseMode.HTML)
    else:
        await message.answer(f"Успешно изменено на: <b>{text}</b>", parse_mode=ParseMode.HTML)

    await dialog_manager.switch_to(state=EditApartmentSG.edit)


async def handle_update_apartment_photos(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    apartment = dialog_manager.start_data
    apartment_id = apartment["apartment_id"]
    
    photos = dialog_manager.dialog_data.get("photos", [])

    # Вызов функции для обновления фотографий
    updated = await repo.bot_apartments.update_apartment_photos(
        tg_id=callback.from_user.id,
        apartment_id=apartment_id,
        photos_ids=photos
    )

    if not updated:
        await callback.message.answer("Не удалось обновить фотографии. Проверьте права доступа.", parse_mode=ParseMode.HTML)
    else:
        await callback.answer("Фотографии успешно обновлены.", parse_mode=ParseMode.HTML)

    await dialog_manager.switch_to(state=EditApartmentSG.edit)


async def handle_update_is_available(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
    **_kwargs,
):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    apartment = dialog_manager.start_data
    apartment_id = apartment["apartment_id"]

    is_available = await repo.bot_apartments.update_is_available(
        tg_id=callback.from_user.id,
        apartment_id=apartment_id,
    )

    if is_available is None:
        await callback.message.answer("Не удалось обновить статус. Проверьте права доступа.")
    else:
        status_text = "✅ Свободно" if is_available else "❌ Занято"
        dialog_manager.dialog_data["is_available"] = status_text
        await callback.answer(f"Статус успешно обновлен на: {status_text}")
        await dialog_manager.switch_to(state=EditApartmentSG.edit, show_mode=ShowMode.EDIT)


async def close_dialog(_, __, dialog_manager: DialogManager, **kwargs):
    await dialog_manager.done()


async def yes_confirm_booking(
    callback: CallbackQuery, widget: Button, dialog_manager: DialogManager
):
    booking: Booking = dialog_manager.dialog_data.get("booking")
    user_id = dialog_manager.dialog_data.get("user_id")
    apartment_id = dialog_manager.dialog_data.get("apartment")["apartment_id"]
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get("scheduler")

    confirm = await repo.apartment_bookings.booking_is_confirmation(
        booking_id=booking.id
    )

    if confirm:
        await bot.send_message(
            chat_id=user_id, text="Поздравляем! ✅ Бронирование успешно подтверждено!"
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
    booking: Booking = dialog_manager.dialog_data.get("booking")
    user_id = dialog_manager.dialog_data.get("user_id")
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