from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy import between, func, select, Result

from src.core.repo.base import BaseRepo
from src.core.models import Users, Landlords, ApartmentPhoto, Apartment, City


class FilterApartmentRepo(BaseRepo):

    async def get_citys(self) -> List[tuple]:

        query = select(City.id, City.name).order_by(City.id) 
        result: Result = await self.session.execute(query)
        citys = result.all()  

        return [(city_id, city_name) for city_id, city_name in citys]
    
    async def get_min_max_price(self, city_id: int) -> tuple:
        query = select(Apartment.price_per_day) \
            .where(Apartment.is_available) \
            .where(Apartment.city_id == city_id) \
            .order_by(Apartment.price_per_day) \
            .limit(1)
        result = await self.session.execute(query)
        min_price = result.scalar()

        query = select(Apartment.price_per_day) \
            .where(Apartment.is_available) \
            .where(Apartment.city_id == city_id) \
            .order_by(Apartment.price_per_day.desc()) \
            .limit(1)
        result = await self.session.execute(query)
        max_price = result.scalar()

        return min_price, max_price
    

    async def no_data_on_apartments(self, city_id: int) -> bool | None:
        query = select(func.count(Apartment.id)).where(Apartment.city_id == city_id)
        result = await self.session.execute(query)
        count = result.scalar()
        
        return count if count > 0 else False
    

    async def check_price_range(self, min_price: float, max_price: float) -> bool:
        query = select(func.count(Apartment.id)).where(Apartment.price_per_day.between(min_price, max_price))
        result = await self.session.execute(query)
        count = result.scalar()

        return count if count > 0 else False


    async def get_rooms(self, city_id: int, price_range: Optional[Tuple[int, int]]) -> List[Tuple[int, int]]:
        # Выбираем количество комнат для апартаментов в указанном городе
        query = select(Apartment.rooms) \
            .where(Apartment.is_available) \
            .where(Apartment.city_id == city_id) \
            .group_by(Apartment.rooms)

        # Если указан диапазон цен, добавляем условие на фильтрацию по цене
        if price_range:
            query = query.where(between(Apartment.price_per_day, price_range[0], price_range[1]))

        result = await self.session.execute(query)
        rooms = result.scalars().all()  # Извлекаем только номера комнат

        # Возвращаем список кортежей (номер комнаты, индекс)
        return [(room, idx) for idx, room in enumerate(rooms, start=1)]
    

    async def filter_apartments(
            self,
            city_id: Optional[int] = None,
            price_range: Optional[tuple] = None,  # (min_price, max_price)
            room: Optional[int] = None
        ) -> List[dict]:
        query = (
            select(Apartment, ApartmentPhoto, Users.tg_id, Users.chat_id, City.name, Landlords)
            .outerjoin(ApartmentPhoto, ApartmentPhoto.apartment_id == Apartment.id)
            .join(Landlords, Landlords.id == Apartment.landlord_id) 
            .join(Users, Users.id == Landlords.user_id)
            .join(City, City.id == Apartment.city_id)
            .where(Apartment.is_available)  
            .order_by(Apartment.id.desc())
        )

        if city_id:
            query = query.where(Apartment.city_id == city_id)
        if price_range:
            query = query.where(Apartment.price_per_day.between(price_range[0], price_range[1]))
        if room:
            query = query.where(Apartment.rooms == room)

        result = await self.session.execute(query)
        apartments = result.all()
        
        if not apartments or not any(apartment for apartment, *_ in apartments):
            return False

        formatted_result = []
        for apartment, photo, landlord_tg_id, chat_id,city_name, landlord in apartments:
            formatted_result.append({
                "apartment_id": apartment.id,
                "landlord_tg_id": landlord_tg_id,
                "landlord_chat_id": chat_id,
                "landlord": landlord,
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
    

    async def update_click_contact_apartment(self, apartment_id: int) -> bool:
        stmt = select(Apartment).where(Apartment.id == apartment_id)
        landlord: Apartment = await self.session.scalar(stmt)

        current_month = datetime.now().strftime("%m-%Y")

        new_count_clicks_phone = landlord.count_contact_views.copy() if landlord.count_contact_views else {}

        if current_month in new_count_clicks_phone:
            new_count_clicks_phone[current_month] += 1
        else:
            new_count_clicks_phone[current_month] = 1

        landlord.count_contact_views = new_count_clicks_phone

        await self.session.flush()
        await self.session.commit()

