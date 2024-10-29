from aiogram.types import ContentType
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.input import TextInput

from src.core.config import config
from src.core.models.landlords import Landlords
from src.core.repo.requests import RequestsRepo



async def getter_get_city(dialog_manager: DialogManager, **kwargs) -> dict:
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    citys = await repo.filter_apartments.get_citys()  
    dialog_manager.dialog_data["citys"] = citys  
    return {"citys": citys}


async def getter_min_max_price(dialog_manager: DialogManager, **kwargs) -> dict:
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")

    min_price: TextInput = dialog_manager.find("min_price").get_value()
    max_price: TextInput = dialog_manager.find("max_price").get_value()

    tuple_price_range = (min_price, max_price)
    dialog_manager.dialog_data["price_range"] = tuple_price_range

    return {
        "count": True,
        "min_price": min_price,
        "max_price": max_price,
    }


async def getter_get_rooms(dialog_manager: DialogManager, **kwargs) -> dict:
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")

    price_range = dialog_manager.dialog_data.get("price_range")
    city_id = dialog_manager.dialog_data.get("city_id")

    count = await repo.filter_apartments.check_price_range(min_price=float(price_range[0]), max_price=float(price_range[1]))
    if not count:
        return {"count": count}

    rooms = await repo.filter_apartments.get_rooms(city_id=int(city_id), price_range=price_range) 
    dialog_manager.dialog_data["rooms"] = rooms  
    
    return {"rooms": rooms}


async def getter_filters(dialog_manager: DialogManager, **kwargs) -> dict:
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")

    count = dialog_manager.dialog_data.get("count")
    if not count:
        return {"count": count}

    city_id = dialog_manager.dialog_data.get("city_id")
    price_range = dialog_manager.dialog_data.get("price_range")
    room = dialog_manager.dialog_data.get("room")


    return  {
        "count": True,
        "city": city_id,
        "price_range": price_range,
        "room": room
    }


async def getter_apartments_data(dialog_manager: DialogManager, **kwargs) -> dict:
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    filters = {
        "city_id": dialog_manager.start_data.get("city_id", None),
        "price_range": dialog_manager.start_data.get("price_range", None),
        "room": dialog_manager.start_data.get("room", None),
    }

    apartments = await repo.filter_apartments.filter_apartments(
        city_id=int(filters.get("city_id")),
        price_range=filters.get("price_range"),
        room=int(filters.get("room"))
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

    return {
        "data": True,
        "is_apartments": True if len(apartments) > 1 else False,
        "media": media,
        "apartment": apartment,
        "count_page": len(apartments),
        "current_page": current_page,
        "server_address": f"{config.api.host}:{config.api.port}",
    }


async def getter_landlord_info(dialog_manager: DialogManager, **kwargs) -> dict:
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")

    apartment = dialog_manager.dialog_data.get("apartment", [])
    landlord: Landlords = apartment["landlord"]
    tg_id = apartment["landlord_tg_id"]
    # info: Landlords = await repo.bot_apartments.landlord_info(id=landlord_id)

    return {
        "name":landlord.company_name,
        "phone": landlord.phone,
        "tg_id": tg_id
    }

