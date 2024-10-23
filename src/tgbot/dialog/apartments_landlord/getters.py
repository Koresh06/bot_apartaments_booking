from aiogram.types import ContentType, User
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.common import ManagedScroll
from aiogram_dialog.widgets.input import TextInput

from src.core.models.bookings import Booking
from src.core.models.landlords import Landlords
from src.core.repo.requests import RequestsRepo


async def getter_get_city(dialog_manager: DialogManager, **kwargs) -> dict:
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")

    citys = await repo.filter_apartments.get_citys()  
    dialog_manager.dialog_data["citys"] = citys 
    return {"citys": citys}


async def start_getters(
    dialog_manager: DialogManager,
    event_from_user: User,
    **kwargs,
):
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    check_landlord: Landlords = await repo.bot_apartments.check_landlord(
        dialog_manager.event.from_user.id
    )

    return {"landlord": check_landlord, "not_landlord": not check_landlord}


async def getter_information_registration(dialog_manager: DialogManager, **kwargs):
    name: TextInput = dialog_manager.find("name").get_value()
    phone: TextInput = dialog_manager.dialog_data.get("phone")

    return {
        "name": name,
        "phone": phone,
    }



async def getter_get_media(dialog_manager: DialogManager, **kwargs) -> dict:
    scroll: ManagedScroll = dialog_manager.find("pages")
    media_number = await scroll.get_page()
    photos = dialog_manager.dialog_data.get("photos", [])
    if photos:
        photo = photos[media_number]
        media = MediaAttachment(
            file_id=MediaId(*photo),
            type=ContentType.PHOTO,
        )
    else:
        media = MediaAttachment(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Image_not_available.png/800px-Image_not_available.png?20210219185637",  # noqa: E501
            type=ContentType.PHOTO,
        )
    return {
        "confirm": False if photos == [] else True,
        "media_count": len(photos),
        "media_number": media_number + 1,
        "media": media,
        "city": dialog_manager.dialog_data.get("city"),
        "street": dialog_manager.find("street").get_value(),
        "house_number": dialog_manager.find("house_number").get_value(),
        "apartment_number": dialog_manager.find("apartment_number").get_value(),
        "price_per_day": dialog_manager.find("price_per_day").get_value(),
        "rooms": dialog_manager.find("rooms").get_value(),
        "description": dialog_manager.find("description").get_value(),
    }


async def getter_catalog_landlord_apartments(dialog_manager: DialogManager, event_from_user: User, **kwargs) -> dict:
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    apartments = await repo.bot_apartments.get_catalog_apartments_landlord(tg_id=event_from_user.id)

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
        type=ContentType.PHOTO,
        )
    return {
        "data": True,
        "is_apartments": True if len(apartments) > 1 else False,
        "media": media,
        "apartment": apartment,
        "count_page": len(apartments),
        "current_page": current_page,

    }


async def getter_apartment_details(dialog_manager: DialogManager, **kwargs) -> dict:
    current_page = dialog_manager.dialog_data.get("page", 1)
    scroll: ManagedScroll = dialog_manager.find("pages")
    media_number = await scroll.get_page()
    # Получаем предыдущую страницу для сравнения
    previous_page = dialog_manager.dialog_data.get("previous_page", 1)
    # Сброс media_number, если текущая страница изменилась
    if current_page != previous_page:
        media_number = 0  # Или 1, если хотите начинать с первого элемента
    # Обновляем предыдущую страницу
    dialog_manager.dialog_data["previous_page"] = current_page
    photos = dialog_manager.dialog_data.get("photos", [])
    apartment = dialog_manager.dialog_data.get("apartment", [])
    # Проверка на наличие фото
    if photos:
        photo = photos[media_number]  # Используем media_number
        media = MediaAttachment(
            file_id=MediaId(*photo),
            type=ContentType.PHOTO,
        )
    else:
        media = None  # Обработка случая, если фото отсутствуют
    return {
        "media_count": len(photos),
        "media_number": media_number + 1,  # Отображаем 1, если нужно
        "media": media,
        "apartment": apartment,
    }


async def getter_edit_apartment(dialog_manager: DialogManager, **kwargs) -> dict:
    apartment = dialog_manager.start_data
    return {"apartment": apartment}


async def getter_edit_apartment_photos(dialog_manager: DialogManager, **kwargs) -> dict:
    apartmet = dialog_manager.start_data
    photos = apartmet["photos"]
    scroll: ManagedScroll = dialog_manager.find("pages")
    media_number = await scroll.get_page()
    photo = photos[media_number]
    media = MediaAttachment(
        file_id=MediaId(*photo),
        type=ContentType.PHOTO,
    )
    
    return {
        "media_count": len(photos),
        "media_number": media_number + 1,  # Отображаем 1, если нужно
        "media": media,
    }

async def getter_confirm_edit_photos(dialog_manager: DialogManager, **kwargs) -> dict:
    scroll: ManagedScroll = dialog_manager.find("pages")
    media_number = await scroll.get_page()
    photos = dialog_manager.dialog_data.get("photos", [])
    if photos:
        photo = photos[media_number]
        media = MediaAttachment(
            file_id=MediaId(*photo),
            type=ContentType.PHOTO,
        )
    else:
        media = MediaAttachment(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Image_not_available.png/800px-Image_not_available.png?20210219185637",  # noqa: E501
            type=ContentType.PHOTO,
        )
    confirm = False if photos == [] else True
    return {
        "confirm": confirm,
        "media_count": len(photos),
        "media_number": media_number + 1,
        "media": media,
        "text": not confirm
    }


async def getter_is_available(dialog_manager: DialogManager, **kwargs) -> dict:
    apartment = dialog_manager.start_data
    one_is_available = apartment["is_available"]
    is_available = dialog_manager.dialog_data.get("is_available")
    if is_available is None:
        is_available = one_is_available
    return {
        "is_available": is_available,
        "apartment_id": apartment["apartment_id"],
    }



async def getter_orders_booking(dialog_manager: DialogManager, event_from_user: User, **kwargs) -> dict:
    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    apartments = await repo.bot_apartments.get_orders_bookings(tg_id=event_from_user.id)

    if not apartments:
        return {"data": apartments}
    
    dialog_manager.dialog_data["count_page"] = len(apartments)
    current_page = dialog_manager.dialog_data.get("page", 1)
    apartment = apartments[current_page - 1]
    dialog_manager.dialog_data["apartment"] = apartment
    
    booking: Booking = apartment["booking"]
    dialog_manager.dialog_data["booking"] = booking

    dialog_manager.dialog_data["user_id"] = apartment["landlord_tg_id"]

    return {
        "data": True,
        "apartment": apartment,
        "count_page": len(apartments),
        "current_page": current_page,
        "booking": booking,
    }