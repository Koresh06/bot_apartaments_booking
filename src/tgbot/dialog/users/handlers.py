from typing import Any
from aiogram import Bot
from aiogram.types import Message
from aiogram.enums.parse_mode import ParseMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import SwitchTo, Button
from aiogram_dialog import DialogManager, StartMode


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
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
) -> None:
    await message.answer("Регистрация успешна!")