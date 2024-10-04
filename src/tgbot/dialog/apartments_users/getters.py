from aiogram.types import ContentType, CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.input import TextInput

from src.core.repo.requests import RequestsRepo
from src.tgbot.dialog.apartments_users.states import FiltersApartmentsSG


async def getter_get_city(dialog_manager: DialogManager, **kwargs) -> dict:
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    citys = await repo.filter_apartments.get_citys()  
    dialog_manager.dialog_data["citys"] = citys  
    return {"citys": citys}


async def getter_min_max_price(dialog_manager: DialogManager, **kwargs) -> dict:
    min_price: TextInput = dialog_manager.find("min_price").get_value()
    max_price: TextInput = dialog_manager.find("max_price").get_value()

    tuple_price_range = (min_price, max_price)
    dialog_manager.dialog_data["price_range"] = tuple_price_range

    return {
        "min_price": min_price,
        "max_price": max_price,
    }


async def getter_get_rooms(dialog_manager: DialogManager, **kwargs) -> dict:
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")

    rooms = await repo.filter_apartments.get_rooms() 
    dialog_manager.dialog_data["rooms"] = rooms  
    return {"rooms": rooms}


async def getter_apartments_data(dialog_manager: DialogManager, **kwargs) -> dict:
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    filters = {
        "city_id": dialog_manager.start_data.get("city_id", None),
        "price_range": dialog_manager.start_data.get("price_range", None),
        "rooms": dialog_manager.start_data.get("room", None),
    }
    apartments = await repo.filter_apartments.filter_apartments(
        city_id=int(filters["city_id"]) if filters["city_id"] is not None else None,
        street=filters.get("street"),
        price_range=filters.get("price_range"),
        rooms=filters.get("rooms")
    )

    if not apartments:
        return {"data": apartments}
        
    dialog_manager.dialog_data["count_page"] = len(apartments)
    current_page = dialog_manager.dialog_data.get("page", 1)
    apartment = apartments[current_page - 1]
    dialog_manager.dialog_data["apartment"] = apartment
    photos = apartment["photos"]
    dialog_manager.dialog_data["photos"] = photos
    photo = photos[0]
    media = MediaAttachment(
        file_id=MediaId(*photo), 
        type=ContentType.PHOTO
    )

    check_filters = any([
        filters["city_id"] is not None,
        filters["price_range"] is not None,
        filters["rooms"] is not None
    ])

    return {
        "data": True,
        "check_filters": check_filters,
        "is_apartments": True if len(apartments) > 1 else False,
        "media": media,
        "apartment": apartment,
        "count_page": len(apartments),
        "current_page": current_page,
    }
