from typing import List, Optional

from sqlalchemy import delete, select, Result, and_
from sqlalchemy.orm import joinedload
from src.core.models import Users, Landlords, ApartmentPhoto, Apartment

from src.core.repo.base import BaseRepo


class FilterApartmentRepo(BaseRepo):

    async def get_citys(self) -> List[tuple]:
        query = select(Apartment.city).distinct().where(Apartment.is_available == True)
        result: Result = await self.session.execute(query)

        cities = result.scalars().all()
        return [(city, index) for index, city in enumerate(cities, start=1)]
    

    async def get_rooms(self) -> List[tuple]:
        query = select(Apartment.rooms).distinct().where(Apartment.is_available == True)
        result: Result = await self.session.execute(query)

        rooms = result.scalars().all()
        return [(room, index) for index, room in enumerate(rooms, start=1)]


    async def filter_apartments(
        self,
        city: Optional[str] = None,
        street: Optional[str] = None,
        price_range: Optional[tuple] = None,  # (min_price, max_price)
        rooms: Optional[int] = None
    ) -> List[dict]:
        query = (
            select(Apartment, ApartmentPhoto)
            .outerjoin(ApartmentPhoto, ApartmentPhoto.apartment_id == Apartment.id)
            .where(Apartment.is_available == True)  # Проверяем статус
        )
        
        if city:
            query = query.where(Apartment.city == city)
        if street:
            query = query.where(Apartment.street == street)
        if price_range:
            query = query.where(Apartment.price_per_day.between(price_range[0], price_range[1]))
        if rooms:
            query = query.where(Apartment.rooms == rooms)

        result = await self.session.execute(query)
        apartments = result.all()

        formatted_result = []
        for apartment, photo in apartments:
            formatted_result.append({
                "apartment_id": apartment.id,
                "city": apartment.city,
                "street": apartment.street,
                "house_number": apartment.house_number,
                "apartment_number": apartment.apartment_number,
                "price_per_day": apartment.price_per_day,
                "rooms": apartment.rooms,
                "description": apartment.description,
                "is_available": apartment.is_available,
                "photos": photo.photos_ids
            })

        return formatted_result
