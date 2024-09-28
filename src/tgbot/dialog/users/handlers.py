from typing import Any
from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from aiogram.enums.parse_mode import ParseMode
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import SwitchTo, Button
from aiogram_dialog import DialogManager, StartMode

from src.core.repo.requests import RequestsRepo





async def error_name_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    error: ValueError,
):
    await message.answer(text="Вы ввели некорректное имя. Попробуйте еще раз")


async def correct_name_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
) -> None:
    await message.answer("Ваше имя: " + text)
    await dialog_manager.next()


async def error_phone_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    error: ValueError,
):
    await message.answer(text="Вы ввели некорректный телефон. Попробуйте еще раз")


async def correct_phone_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
) -> None:
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
    await dialog_manager.done()