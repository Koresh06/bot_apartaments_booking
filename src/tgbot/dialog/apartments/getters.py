from aiogram.types import CallbackQuery, ContentType, User
from aiogram_dialog import Dialog, DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.common import ManagedScroll

from src.core.repo.requests import RequestsRepo


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
        "city": dialog_manager.find("city").get_value(),
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
    dialog_manager.dialog_data["count_page"] = len(apartments)

    current_page = dialog_manager.dialog_data.get("page", 1)
    apartment = apartments[current_page - 1]

    dialog_manager.dialog_data["apartment"] = apartment

    photos = apartment["photos"]
    dialog_manager.dialog_data["photos"] = photos
    photo = photos[0]
    print(photo)
    media = MediaAttachment(
    file_id=MediaId(*photo),
    type=ContentType.PHOTO,
    )

    return {
        "count_apartments": True if len(apartments) > 1 else False,
        "media": media,
        "apartment": apartment,
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
    print(media_number)
    photos = dialog_manager.dialog_data.get("photos", [])
    print(photos)
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
    }


