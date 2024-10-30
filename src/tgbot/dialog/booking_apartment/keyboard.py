from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.core.models import Landlords


class PhoneCbData(CallbackData, prefix="calendar"):
    landlord_id: int
    tg_id: int
    name: str
    phone: str





async def landlord_keyboard(landlord: Landlords, tg_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    cb = PhoneCbData(landlord_id=landlord.id, tg_id=tg_id, name=landlord.company_name, phone=landlord.phone)
    builder.row(InlineKeyboardButton(text="🏠 Арендодатель", callback_data=cb.pack()))

    return builder.as_markup()


async def phone_keyboard(tg_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="📞 Контакт", url=f"tg://user?id={tg_id}"))

    return builder.as_markup()