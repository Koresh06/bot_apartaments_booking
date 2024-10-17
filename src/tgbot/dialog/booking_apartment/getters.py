from aiogram_dialog import DialogManager

from src.core.repo.requests import RequestsRepo


async def getter_date_and_booked_dates(dialog_manager: DialogManager, **_kwargs):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    start_date = dialog_manager.dialog_data.get("start_date")
    end_date = dialog_manager.dialog_data.get("end_date")

    apartment = dialog_manager.start_data.get("apartment")
    bookings = await repo.apartment_bookings.get_current_date_bookings(apartment_id=apartment["apartment_id"])

    dialog_manager.dialog_data["bookings"] = bookings
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        "bookings": bookings,
        "apartment": apartment,
    }

