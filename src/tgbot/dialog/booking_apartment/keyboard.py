from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.core.models import Landlords




class PhoneCbData(CallbackData, prefix="calendar"):
    id: int
    name: str
    phone: str



async def phone_keyboard(landlord: Landlords) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    cb = PhoneCbData(id=landlord.id, name=landlord.company_name, phone=landlord.phone)
    builder.add(InlineKeyboardButton(text="📞 Телефон", callback_data=cb.pack()))

    return builder.as_markup()
    