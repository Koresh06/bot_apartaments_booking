from datetime import date
from typing import Dict

from babel.dates import get_day_names, get_month_names

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import (
    Calendar,
    CalendarScope,
)
from aiogram_dialog.widgets.kbd.calendar_kbd import (
    CalendarDaysView,
    CalendarMonthView,
    CalendarScopeView,
    CalendarYearsView,
    DATE_TEXT,
    TODAY_TEXT,
)
from aiogram_dialog.widgets.text import Format, Text


SELECTED_DAYS_KEY = "selected_dates"


class WeekDay(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: date = data["date"]
        locale = manager.event.from_user.language_code
        return get_day_names(
            width="short",
            context="stand-alone",
            locale=locale,
        )[selected_date.weekday()].title()


class MarkedDay(Text):
    def __init__(self, mark: str, other: Text, busy_mark: str = "🚫"):
        super().__init__()
        self.mark = mark
        self.other = other
        self.busy_mark = busy_mark  # эмодзи для занятых дат

    async def _render_text(self, data, manager: DialogManager) -> str:
        current_date: date = data["date"]
        serial_date = current_date.isoformat()
        selected = manager.dialog_data.get(SELECTED_DAYS_KEY, [])
        today = date.today()

        # Получаем список бронирований
        bookings = manager.dialog_data.get("bookings", [])

        # Если список бронирований не пустой, проверяем занятость
        if bookings:
            for booking in bookings:
                booking_start_date = booking["booking"].start_date.date()  # Приводим к типу date
                booking_end_date = booking["booking"].end_date.date()  # Приводим к типу date
                if booking_start_date <= current_date <= booking_end_date:
                    return self.busy_mark  # Если дата занята, возвращаем эмодзи занятости

        if current_date < today:
            return "❌"  # Прошедшие даты
        elif serial_date in selected:
            return self.mark  # Выбранные пользователем даты
        return await self.other.render_text(data, manager)


class Month(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: date = data["date"]
        locale = manager.event.from_user.language_code
        return get_month_names(
            "wide",
            context="stand-alone",
            locale=locale,
        )[selected_date.month].title()


class CustomCalendar(Calendar):
    def _init_views(self) -> Dict[CalendarScope, CalendarScopeView]:
        return {
            CalendarScope.DAYS: CalendarDaysView(
                self._item_callback_data,
                date_text=MarkedDay("🔴", DATE_TEXT, busy_mark="🚫"),  # Эмодзи для занятых дней
                today_text=MarkedDay("⭕", TODAY_TEXT, busy_mark="🚫"),  # Эмодзи для занятых дней
                header_text="~~~~~ " + Month() + " ~~~~~",
                weekday_text=WeekDay(),
                next_month_text=Month() + " >>",
                prev_month_text="<< " + Month(),
            ),
            CalendarScope.MONTHS: CalendarMonthView(
                self._item_callback_data,
                month_text=Month(),
                header_text="~~~~~ " + Format("{date:%Y}") + " ~~~~~",
                this_month_text="[" + Month() + "]",
            ),
            CalendarScope.YEARS: CalendarYearsView(
                self._item_callback_data,
            ),
        }

