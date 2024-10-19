from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from src.core.models import Apartment

from src.core.repo.base import BaseRepo


class ApartmentApiRepo(BaseRepo):
    
    # async def get_apartments_by_landlord_id(self, landlord_id: int):
    #     query = (
    #         select(Apartment)
    #         .options(
    #             selectinload(Apartment.city_rel),  # Загружаем город
    #             selectinload(Apartment.photos_rel)  # Загружаем фотографии
    #         )
    #         .where(Apartment.landlord_id == landlord_id)
    #         .order_by(Apartment.id.desc())  # Условие на  landlord_id
    #     )
    #     result = await self.session.execute(query)
    #     apartments = result.scalars().all()  # Получаем все найденные квартиры

    #     # Цикл для вывода всех данных
    #     for apartment in apartments:
    #         print(f"Apartment ID: {apartment.id}")
    #         print(f"Landlord ID: {apartment.landlord_id}")
    #         print(f"City: {apartment.city_rel.name}")  # Предполагается, что у  модели City есть поле name
    #         print(f"Street: {apartment.street}")
    #         print(f"Price per day: {apartment.price_per_day}")
    #         print(f"Description: {apartment.description}")
    #         print(f"Photos:")

    #         for photo in apartment.photos_rel:
    #             print(f"- Photo ID: {photo.id}, URL: {await get_photos_urls(photo.photos_ids)}")  #   Предполагается, что у фотографии есть URL

    #         print("="*50)  # Разделитель для каждой квартиры

    #     return apartments


    async def get_paginated_apartments(self, page: int, size: int):
        offset = (page - 1) * size
        query = (
            select(Apartment)
            .options(
                selectinload(Apartment.city_rel),
                selectinload(Apartment.landlord_rel)
            )
            .order_by(Apartment.id.desc())  # Условие на  landlord_id
            .offset(offset)
            .limit(size)
        )
        result = await self.session.execute(query)
        apartments = result.scalars().all()  # Получаем все найденные квартиры

        return apartments
    

    async def count_all_apartments(self):
        query = select(func.count(Apartment.id))
        result = await self.session.execute(query)
        total = result.scalar()

        return total
    

    async def get_apartment_by_landlord(self, landlord_id: int):
        query = (
            select(Apartment)
            .options(
                selectinload(Apartment.city_rel),
                selectinload(Apartment.landlord_rel)
            )
            .where(Apartment.landlord_id == landlord_id)
        )
        result = await self.session.execute(query)
        apartments = result.scalars().all()  # Получаем все найденные квартиры

        return apartments