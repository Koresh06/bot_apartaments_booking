from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from src.core.models import Apartment, Booking

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