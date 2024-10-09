from datetime import date
from typing import Optional

from sqlalchemy import select
from src.core.models import Users, Apartment, Booking, City

from src.core.repo.base import BaseRepo



class StatisticsApiRepo(BaseRepo):

    async def get_general_statistics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ):
        # Получаем количество всех пользователей
        stmt_users = select(Users)
        result_users = await self.session.execute(stmt_users)
        users = result_users.scalars().all()
        total_users = len(users) if users else "Нет данных"

        # Получаем все апартаменты
        stmt_apartments = select(Apartment)
        result_apartments = await self.session.execute(stmt_apartments)
        apartments = result_apartments.scalars().all()
        total_apartments = len(apartments) if apartments else "Нет данных"

        # Получаем завершённые бронирования
        stmt_completed_bookings = select(Booking).where(
            Booking.is_completed == True,
        )

        if start_date:
            stmt_completed_bookings = stmt_completed_bookings.where(
                Booking.create_at >= start_date
            )
        if end_date:
            stmt_completed_bookings = stmt_completed_bookings.where(
                Booking.create_at <= end_date
            )

        result_completed = await self.session.execute(stmt_completed_bookings)
        completed_bookings = result_completed.scalars().all()
        total_completed_bookings = (
            len(completed_bookings) if completed_bookings else "Нет данных"
        )

        # Получаем ожидающие бронирования
        stmt_pending_bookings = select(Booking).where(
            Booking.is_completed == False,
        )

        if start_date:
            stmt_pending_bookings = stmt_pending_bookings.where(
                Booking.create_at >= start_date
            )
        if end_date:
            stmt_pending_bookings = stmt_pending_bookings.where(
                Booking.create_at <= end_date
            )

        result_pending = await self.session.execute(stmt_pending_bookings)
        pending_bookings = result_pending.scalars().all()
        total_pending_bookings = (
            len(pending_bookings) if pending_bookings else "Нет данных"
        )

        # Подсчитываем общий доход
        total_income = 0
        for booking in completed_bookings:
            # Находим соответствующий апартамент
            apartment = next(
                (apt for apt in apartments if apt.id == booking.apartment_id), None
            )
            if apartment:
                # Вычисляем доход на основе продолжительности бронирования и цены за день
                days_booked = (booking.end_date - booking.start_date).days
                total_income += apartment.price_per_day * days_booked

        total_income = total_income if total_income > 0 else "Нет данных"

        return {
            "total_users": total_users,
            "total_apartments": total_apartments,
            "total_completed_bookings": total_completed_bookings,
            "total_pending_bookings": total_pending_bookings,
            "total_income": total_income,
        }
    
    async def get_pending_bookings(self):
        stmt = (
            select(
                Booking,
                Users.username,
                Apartment.street,
                Apartment.house_number,
                Apartment.apartment_number,
                City.name.label('city_name')
            )
            .join(Users, Booking.user_id == Users.id) 
            .join(Apartment, Booking.apartment_id == Apartment.id)  
            .join(City, Apartment.city_id == City.id) 
            .where(Booking.is_completed == False)  
            .order_by(Booking.id.desc())
        )
        result = await self.session.execute(stmt)
        bookings_with_details = result.all()  
        return bookings_with_details
    

    async def get_completed_bookings(self):
        stmt = (
            select(
                Booking,
                Users.username,
                Apartment.street,
                Apartment.house_number,
                Apartment.apartment_number,
                City.name.label('city_name')
            )
            .join(Users, Booking.user_id == Users.id) 
            .join(Apartment, Booking.apartment_id == Apartment.id)  
            .join(City, Apartment.city_id == City.id) 
            .where(Booking.is_completed == True)  
            .order_by(Booking.id.desc())
        )
        result = await self.session.execute(stmt)
        bookings_with_details = result.all()  
        return bookings_with_details


    async def get_total_income_bookings(self):
        # Выполняем запрос для получения завершенных бронирований с деталями
        stmt = (
            select(
                Booking,
                Users.username,
                Apartment.street,
                Apartment.house_number,
                Apartment.apartment_number,
                City.name.label('city_name'),
                Apartment.price_per_day,  # Получаем цену за день
            )
            .join(Users, Booking.user_id == Users.id)  # Присоединение пользователей
            .join(Apartment, Booking.apartment_id == Apartment.id)  # Присоединение апартаментов
            .join(City, Apartment.city_id == City.id)  # Присоединение городов
            .where(Booking.is_completed == True)  # Только завершенные бронирования
            .order_by(Booking.id.desc())
        )
        
        result = await self.session.execute(stmt)
        bookings_with_details = result.all()  # Получаем список кортежей

        bookings_with_income = []

        # Проходим по всем бронированиям
        for booking, username, street, house_number, apartment_number, city_name, price_per_day in bookings_with_details:
            # Вычисляем количество дней бронирования
            days_booked = (booking.end_date - booking.start_date).days

            # Считаем доход за бронирование
            booking_income = price_per_day * days_booked

            # Добавляем информацию в список с доходом
            bookings_with_income.append({
                'booking': booking,
                'username': username,
                'street': street,
                'house_number': house_number,
                'apartment_number': apartment_number,
                'city_name': city_name,
                'income': booking_income,  # Доход за конкретное бронирование
                'created_at': booking.create_at  # Дата создания апартамента
            })


        return bookings_with_income





