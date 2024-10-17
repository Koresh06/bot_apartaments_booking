from typing import List, Optional
from sqlalchemy import select, Result

from src.core.repo.base import BaseRepo
from src.core.models import Users, Landlords, ApartmentPhoto, Apartment, City


class FilterApartmentRepo(BaseRepo):

    async def get_citys(self) -> List[tuple]:

        query = select(City.id, City.name).order_by(City.id) 
        result: Result = await self.session.execute(query)

        citys = result.all()  
        return [(city_name, city_id) for city_id, city_name in citys]


    async def get_rooms(self) -> List[tuple]:
        query = select(Apartment.rooms).distinct().where(Apartment.is_available)
        result: Result = await self.session.execute(query)

        rooms = result.scalars().all()
        return [(room, index) for index, room in enumerate(rooms, start=1)]


    async def filter_apartments(
            self,
            city_id: Optional[int] = None,
            street: Optional[str] = None,
            price_range: Optional[tuple] = None,  # (min_price, max_price)
            rooms: Optional[int] = None
        ) -> List[dict]:
        query = (
            select(Apartment, ApartmentPhoto, Users.tg_id, Users.chat_id, City.name)
            .outerjoin(ApartmentPhoto, ApartmentPhoto.apartment_id == Apartment.id)
            .join(Landlords, Landlords.id == Apartment.landlord_id) 
            .join(Users, Users.id == Landlords.user_id)
            .join(City, City.id == Apartment.city_id)
            .where(Apartment.is_available)  
            .order_by(Apartment.id.desc())
        )

        if city_id:
            query = query.where(Apartment.city_id == city_id)
        if street:
            query = query.where(Apartment.street == street)
        if price_range:
            query = query.where(Apartment.price_per_day.between(price_range[0], price_range[1]))
        if rooms:
            query = query.where(Apartment.rooms == rooms)

        result = await self.session.execute(query)
        apartments = result.all()
        
        if not apartments or not any(apartment for apartment, *_ in apartments):
            return False

        formatted_result = []
        for apartment, photo, landlord_tg_id, chat_id,city_name in apartments:
            formatted_result.append({
                "apartment_id": apartment.id,
                "landlord_tg_id": landlord_tg_id,
                "landlord_chat_id": chat_id,
                "city": city_name,
                "street": apartment.street,
                "house_number": apartment.house_number,
                "apartment_number": apartment.apartment_number if apartment.apartment_number else "-",
                "price_per_day": apartment.price_per_day,
                "rooms": apartment.rooms,
                "description": apartment.description,
                "is_available": apartment.is_available,
                "photos": photo.photos_ids if photo else []
            })

        return formatted_result


