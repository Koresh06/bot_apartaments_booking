from aiogram.types import CallbackQuery, Message
from aiogram.enums.parse_mode import ParseMode
from aiogram_dialog import Dialog, DialogManager, StartMode, ShowMode
from aiogram_dialog.widgets.common import ManagedScroll
from aiogram_dialog.widgets.input import MessageInput, ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Button

from src.core.repo.requests import RequestsRepo
from src.tgbot.dialog.apartments.states import MenuLandlordSG, EditApartmentSG


async def error_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
):
    await message.answer(
        text="Вы ввели некоректные данные, убедитесь, что вы правильно ввели необходимые данные"
    )


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
        "city": dialog_manager.find("city").get_value(),
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
        await callback.message.answer("Не удалось обновить статус. Проверьте права доступа.", parse_mode=ParseMode.HTML)
    else:
        status_text = "✅ Свободно" if is_available else "❌ Занято"
        dialog_manager.dialog_data["is_available"] = status_text
        await callback.answer(f"Статус успешно обновлен на: <b>{status_text}</b>", parse_mode=ParseMode.HTML)
        await dialog_manager.switch_to(state=EditApartmentSG.edit, show_mode=ShowMode.EDIT)




async def close_dialog(_, __, dialog_manager: DialogManager, **kwargs):
    await dialog_manager.done()