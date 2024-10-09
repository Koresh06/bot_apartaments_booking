
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.core.models import Apartment, Booking

from src.core.repo.base import BaseRepo


class BookingApiRepo(BaseRepo):
    
    async def get_all_bookings(self):
        stmt = (
            select(Booking)
            .options(
                selectinload(Booking.user_rel),       # Подгружаем пользователя
                selectinload(Booking.apartment_rel)    # Подгружаем квартиру
                .selectinload(Apartment.landlord_rel)  # Подгружаем арендодателя через квартиру
            )
            .order_by(Booking.id.desc())
        )
        
        # Получаем все бронирования
        result = await self.session.execute(stmt)
        bookings = result.scalars().all() 

        if not bookings:  
            return "Нет доступных бронирований"
        
        return bookings 