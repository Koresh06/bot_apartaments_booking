from typing import List, Optional

from sqlalchemy import delete, select
from src.core.models import Users, Landlords, ApartmentPhoto, Apartment

from src.core.repo.base import BaseRepo


class BotApartmentRepo(BaseRepo):

    async def check_landlord(self, tg_id: int) -> bool:
        result = await self.session.scalar(
            select(Landlords).join(Users).where(Users.tg_id == tg_id)
        )

        return result is not None

    async def register_apartment_landlord(self, tg_id: int, data: dict) -> bool:
        # Получение владельца квартиры по tg_id
        stmt: Landlords = await self.session.scalar(
            select(Landlords).join(Users).where(Users.tg_id == tg_id)
        )

        params = Apartment(
            landlord_id=stmt.id,
            city=data["city"],
            street=data["street"],
            house_number=data["house_number"],
            apartment_number=data["apartment_number"],
            price_per_day=data["price_per_day"],
            rooms=data["rooms"],
            description=data["description"],
        )
        self.session.add(params)
        await self.session.commit()
        await self.session.refresh(params)

        photos = ApartmentPhoto(
            apartment_id=params.id,
            photos_ids=data["photos"],
        )
        self.session.add(photos)
        await self.session.commit()
        await self.session.refresh(photos)

        return True

    async def get_catalog_apartments_landlord(self, tg_id: int) -> Optional[List[dict]]:
        # Получение арендодателя по tg_id
        landlord_stmt = await self.session.scalar(
            select(Landlords).join(Users).where(Users.tg_id == tg_id)
        )

        if not landlord_stmt:
            return None  # Если арендодатель не найден, возвращаем None

        # Получение всех апартаментов с фотографиями для арендодателя
        stmt = (
            select(Apartment, ApartmentPhoto)
            .where(Apartment.landlord_id == landlord_stmt.id)
            .outerjoin(ApartmentPhoto, ApartmentPhoto.apartment_id == Apartment.id)
            .order_by(Apartment.id.desc())
        )

        # Выполняем запрос и получаем все результаты
        result = await self.session.execute(stmt)
        apartments = result.all()

        # Форматирование результатов в удобный формат
        formatted_result = []
        for apartment, photo in apartments:
            formatted_result.append(
                {
                    "apartment_id": apartment.id,
                    "landlord_id": apartment.landlord_id,
                    "landlord_tg_id": tg_id,  # Сохраняем tg_id арендодателя
                    "city": apartment.city,
                    "street": apartment.street,
                    "house_number": apartment.house_number,
                    "apartment_number": apartment.apartment_number,
                    "price_per_day": apartment.price_per_day,
                    "rooms": apartment.rooms,
                    "description": apartment.description,
                    "is_available": (
                        "✅ Свободно" if apartment.is_available else "❌ Занято"
                    ),
                    "photos": photo.photos_ids if photo else [],  # Обработка отсутствующих фотографий
                }
            )

        return formatted_result


    async def check_apartment_landlord(
        self,
        tg_id: int,
        apartment_id: int,
    ) -> bool:
        # Получаем информацию о квартире
        apartment_info: Apartment = await self.session.scalar(
            select(Apartment).where(Apartment.id == apartment_id)
        )

        if not apartment_info:
            return None  # Квартира не найдена

        # Проверяем, что пользователь является владельцем квартиры
        landlord_info = await self.session.scalar(
            select(Landlords)
            .where(Landlords.id == apartment_info.landlord_id)
            .join(Users)
            .where(Users.tg_id == tg_id)
        )

        if not landlord_info:
            return None  # Пользователь не является владельцем

        return apartment_info

    async def update_apartment_info(
        self,
        tg_id: int,
        apartment_id: int,
        widget_id: int,
        text: str,
    ) -> bool:

        apartment_info = await self.check_apartment_landlord(
            tg_id=tg_id, apartment_id=apartment_id
        )
        if not apartment_info:
            return False  # Квартира не найдена

        # Обновляем информацию
        if widget_id == "city":
            apartment_info.city = text
        elif widget_id == "street":
            apartment_info.street = text
        elif widget_id == "house_number":
            apartment_info.house_number = text
        elif widget_id == "apartment_number":
            apartment_info.apartment_number = text
        elif widget_id == "price_per_day":
            apartment_info.price_per_day = text
        elif widget_id == "rooms":
            apartment_info.rooms = text
        elif widget_id == "description":
            apartment_info.description = text
        # Добавьте другие условия для дополнительных полей
        await self.session.commit()
        return True  # Успешно обновлено

    async def update_apartment_photos(
        self,
        tg_id: int,
        apartment_id: int,
        photos_ids: List[str],
    ) -> bool:
        apartment_info: Apartment = await self.check_apartment_landlord(
            tg_id=tg_id,
            apartment_id=apartment_id,
        )
        if not apartment_info:
            return False  # Квартира не найдена

        # Удаляем старые фотографии, если необходимо
        await self.session.execute(
            delete(ApartmentPhoto).where(ApartmentPhoto.apartment_id == apartment_id)
        )

        # Добавляем новые фотографии
        new_photo = ApartmentPhoto(apartment_id=apartment_id, photos_ids=photos_ids)
        self.session.add(new_photo)

        await self.session.commit()
        return True  # Успешно обновлено

    async def delete_apartment_landlord(
        self,
        tg_id: int,
        apartment_id: int,
    ) -> bool:
        apartment_info: Apartment = await self.check_apartment_landlord(
            tg_id=tg_id,
            apartment_id=apartment_id,
        )
        if not apartment_info:
            return False  # Квартира не найдена

        # Удаляем все фотографии квартиры
        await self.session.execute(
            delete(ApartmentPhoto).where(ApartmentPhoto.apartment_id == apartment_id)
        )

        # Удаляем квартиру
        await self.session.execute(
            delete(Apartment).where(Apartment.id == apartment_id)
        )

        await self.session.commit()
        return True

    async def update_is_available(
            self,
            tg_id: int,
            apartment_id: int,
        ) -> Optional[bool]:  # Возвращаем True или False
        # Проверяем информацию о квартире
        apartment_info: Apartment = await self.check_apartment_landlord(
            tg_id=tg_id,
            apartment_id=apartment_id,
        )
    
        if apartment_info is None:
            return None  # Квартира не найдена или пользователь не является владельцем
    
        # Изменяем статус доступности
        apartment_info.is_available = not apartment_info.is_available  # Меняем на противоположный статус
    
        # Сохраняем изменения в базе данных
        await self.session.commit()
    
        return apartment_info.is_available  # Возвращаем новый статус


