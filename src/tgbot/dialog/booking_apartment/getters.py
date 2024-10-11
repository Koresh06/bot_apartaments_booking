from aiogram_dialog import DialogManager


async def getter_date(dialog_manager: DialogManager, **_kwargs):
    start_date = dialog_manager.dialog_data.get("start_date")
    end_date = dialog_manager.dialog_data.get("end_date")
    
    return {
        "start_date": start_date,
        "end_date": end_date,
    }


async def getter_confirm_landlord_booking(dialog_manager: DialogManager, **_kwargs):
    apartment = dialog_manager.start_data.get("apartment")

    return {
        "apartment": apartment,
    }