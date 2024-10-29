from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


# class PhoneCbData(CallbackData, prefix="calendar"):
#     id: int
#     name: str
#     phone: str


async def phone_keyboard(tg_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # cb = PhoneCbData(id=landlord.id, name=landlord.company_name, phone=landlord.phone)
    builder.add(InlineKeyboardButton(text="📞 Контакт", url=f"tg://user?id={tg_id}"))

    return builder.as_markup()
    