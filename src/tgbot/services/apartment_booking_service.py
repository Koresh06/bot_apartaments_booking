from datetime import date

from sqlalchemy import select
from src.core.models import Users, Apartment, Booking

from src.core.repo.base import BaseRepo


class ApartmentBookingRepo(BaseRepo):

    async def save_booking(
        self,
        tg_id: int,
        apartment_id: int,
        start_date: date,
        end_date: date,
    ) -> bool:
        # Получение пользователя по user_id
        user_stmt = await self.session.scalar(select(Users).where(Users.tg_id == tg_id))

        if not user_stmt:
            return False  # Если пользователь не найден, возвращаем False

        # Получение квартиры по apartment_id
        apartment_stmt = await self.session.scalar(
            select(Apartment).where(Apartment.id == apartment_id)
        )

        if not apartment_stmt:
            return False  # Если квартира не найдена, возвращаем False

        # Создание объекта бронирования
        booking = Booking(
            user_id=user_stmt.id,
            apartment_id=apartment_stmt.id,
            start_date=start_date,
            end_date=end_date,
        )

        self.session.add(booking)
        await self.session.commit()  # Сохраняем изменения
        await self.session.refresh(booking)  # Обновляем объект с ID

        return booking


    async def booking_confirmation(self, booking_id: int, apartment_id: int) -> bool:
        # Получаем текущее состояние бронирования по его ID
        booking = await self.session.scalar(
            select(Booking).where(Booking.id == booking_id)
        )

        apartment = await self.session.scalar(select(Apartment).where(Apartment.id == apartment_id))

        if booking is None:
            return False  # Бронирование не найдено

        # Изменяем статус бронирования на подтвержденный
        booking.is_confirmed = True  # Устанавливаем поле is_confirmed в True

        # Обновляем информацию о квартире
        apartment.is_available = False  # Устанавливаем поле is_available в False

        # Сохраняем изменения в базе данных
        self.session.add(booking)
        self.session.add(apartment)
        await self.session.commit()

        # Обновляем объект после сохранения
        await self.session.refresh(booking)

        return True  # Возвращаем успех
    

    async def delete_booking(self, booking_id: int, landlord_id: int) -> bool:
        # Получаем текущее состояние бронирования по его ID
        booking = await self.session.scalar(
            select(Booking).where(Booking.id == booking_id)
        )

        if booking is None:
            return False  # Бронирование не найдено
        
        try:
            # Удаляем бронирование
            await self.session.delete(booking)

            # Сохраняем изменения в базе данных
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()  # Откатываем транзакцию в случае ошибки
            raise e  # Перебрасываем исключение для обработки на более высоком уровне

        return True  # Успешно удалено

