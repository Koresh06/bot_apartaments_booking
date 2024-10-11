from datetime import date
import logging
from sqlalchemy import select

from src.core.repo.base import BaseRepo
from src.core.models import Users, Apartment, Booking


class ApartmentBookingRepo(BaseRepo):

    async def save_booking(
        self,
        tg_id: int,
        apartment_id: int,
        start_date: date,
        end_date: date,
    ) -> bool:
        user_stmt = await self.session.scalar(select(Users).where(Users.tg_id == tg_id))

        if not user_stmt:
            return False  

        apartment_stmt = await self.session.scalar(
            select(Apartment).where(Apartment.id == apartment_id)
        )

        if not apartment_stmt:
            return False  
        
        booking = Booking(
            user_id=user_stmt.id,
            apartment_id=apartment_stmt.id,
            start_date=start_date,
            end_date=end_date,
        )

        self.session.add(booking)
        await self.session.commit() 
        await self.session.refresh(booking) 

        return booking


    async def booking_confirmation(self, booking_id: int, apartment_id: int) -> bool:
        booking = await self.session.scalar(
            select(Booking).where(Booking.id == booking_id)
        )

        apartment = await self.session.scalar(select(Apartment).where(Apartment.id == apartment_id))

        if booking is None:
            return False  

        booking.is_confirmed = True 

        apartment.is_available = False 

        self.session.add(booking)
        self.session.add(apartment)
        await self.session.commit()

        await self.session.refresh(booking)

        return True  
    

    async def delete_booking(self, booking_id: int) -> bool:
        booking = await self.session.scalar(
            select(Booking).where(Booking.id == booking_id)
        )
        print(booking)

        if booking is None:
            return False  
        
        try:
            await self.session.delete(booking)

            await self.session.commit()
        except Exception as e:
            await self.session.rollback() 
            raise e 

        return True 


    async def update_booking_status(self, booking_id):
        try:
            booking = await self.session.scalar(select(Booking).where(Booking.id == booking_id))
            
            if booking:
                booking.is_completed = True
                apartment = await self.session.scalar(select(Apartment).where(Apartment.id == booking.apartment_id))

                if apartment:
                    apartment.rating += 1
                    self.session.add(apartment)

                self.session.add(booking)
                await self.session.commit()
                
                logging.info("Статусы бронирований обновлены успешно.")
            else:
                logging.warning(f"Бронирование с ID {booking_id} не найдено.")

        except Exception as e:
            logging.error(f"Ошибка при обновлении статусов бронирований: {e}")
