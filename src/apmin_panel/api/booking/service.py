from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from src.core.models import Apartment, Booking, Landlords

from src.core.repo.base import BaseRepo


class BookingApiRepo(BaseRepo):
    
    async def get_paginated_bookings(self, page: int, size: int):
        offset = (page - 1) * size
        stmt = (
            select(Booking)
            .options(
                selectinload(Booking.user_rel),     
                selectinload(Booking.apartment_rel)   
                .selectinload(Apartment.landlord_rel)  
            )
            .order_by(Booking.id.desc())
            .offset(offset)
            .limit(size)
        )
        
        result = await self.session.execute(stmt)
        bookings = result.scalars().all() 

        if not bookings:  
            return "Нет доступных бронирований"
        
        return bookings 
    
    async def count_all_bookings(self):
        query = select(func.count(Booking.id))
        result = await self.session.execute(query)
        total = result.scalar()

        return total
    

    async def get_landlord_by_apartment(self, apartment_id: int) -> Optional[Landlords]:
        # Запрос на получение апартамента и связанного с ним арендодателя
        stmt = select(Apartment).where(Apartment.id == apartment_id).options(selectinload(Apartment.landlord_rel))
        result = await self.session.execute(stmt)
        apartment = result.scalar()

        # Если апартамент найден, возвращаем связанного арендодателя
        if apartment:
            return apartment.landlord_rel

        return None  # Если апартамент не найден, возвращаем None
