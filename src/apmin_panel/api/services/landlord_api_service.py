from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.core.models import Landlords, Users, Apartment, Booking, City

from src.core.repo.base import BaseRepo
from ..schemas.landlord_schemas import CreateLandlordSchema


class LandlordApiRepo(BaseRepo):

    async def get_all_landlords(self):
        stmt = (
            select(Landlords)
            .options(selectinload(Landlords.user_rel))
            .order_by(Landlords.id.desc())  # Сортируем по ID арендодателя
        )

        result = await self.session.execute(stmt)
        landlords = result.scalars().all()

        if not landlords:
            return "Нет доступных арендодателей"

        return landlords

    

    async def get_statistics_by_landlord_id(
        self,
        landlord_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ):
        # Получаем информацию об арендодателе
        stmt = select(Landlords).join(Users).where(Landlords.id == landlord_id)
        result = await self.session.execute(stmt)
        landlord = result.scalar()

        if not landlord:
            return "Арендодатель не найден"

        # Получаем апартаменты арендодателя
        stmt_apartments = select(Apartment).where(Apartment.landlord_id == landlord_id)
        result_apartments = await self.session.execute(stmt_apartments)
        apartments = result_apartments.scalars().all()

        total_apartments = len(apartments) if apartments else "Нет данных"

        # Получаем завершённые бронирования
        stmt_completed_bookings = select(Booking).where(
            Booking.apartment_id.in_([apartment.id for apartment in apartments]),
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
            Booking.apartment_id.in_([apartment.id for apartment in apartments]),
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
            "landlord": landlord,
            "apartments": apartments,
            "total_apartments": total_apartments,
            "total_completed_bookings": total_completed_bookings,
            "total_pending_bookings": total_pending_bookings,  # Добавлено
            "total_income": total_income,
        }
    

    async def get_completed_bookings_by_landlord_id(self, landlord_id: int):
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
            .where(Apartment.landlord_id == landlord_id)  # Фильтр по ID арендатора
            .order_by(Booking.id.desc())
        )
        result = await self.session.execute(stmt)
        bookings_with_details = result.all()
        return bookings_with_details
    

    async def get_pending_bookings_by_landlord_id(self, landlord_id: int):
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
            .join(Landlords, Apartment.landlord_id == Landlords.id)  # Соединяем с арендодателями
            .where(
                Booking.is_completed == False,
                Landlords.id == landlord_id  # Фильтруем по id арендодателя
            )
            .order_by(Booking.id.desc())
        )
        result = await self.session.execute(stmt)
        bookings_with_details = result.all()
        return bookings_with_details


    async def get_total_income_bookings_by_landlord_id(self, landlord_id: int):
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
            .join(Landlords, Apartment.landlord_id == Landlords.id)  # Соединяем с арендодателями
            .where(
                Booking.is_completed == True,  # Только завершенные бронирования
                Landlords.id == landlord_id  # Фильтруем по id арендодателя
            )
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
                'created_at': booking.create_at  # Дата создания бронирования
            })

        return bookings_with_income
    

    async def get_users_not_landlord(self):
        # Запрос для получения пользователей, которые не являются арендодателями
        stmt = (
            select(Users)
            .outerjoin(Landlords, Users.id == Landlords.user_id)  # Outer join на таблицу Landlords
            .filter(Landlords.user_id.is_(None))  # Фильтруем только тех пользователей, которые не имеют записей в Landlords
        )

        result = await self.session.execute(stmt)
        users_not_landlords = result.scalars().all()  # Получаем список пользователей

        return users_not_landlords
    

    async def create_landlord(self, create_landlord: CreateLandlordSchema):
        try:
            # Проверяем, существует ли уже арендодатель с таким user_id
            existing_landlord = await self.session.execute(
                select(Landlords).filter(Landlords.user_id == create_landlord.user_id)
            )
            if existing_landlord.scalars().first() is not None:
                # Если арендодатель уже существует, выбрасываем ошибку или возвращаем сообщение
                raise ValueError(f"Арендодатель с user_id {create_landlord.user_id} уже существует.")

            # Если арендодатель не существует, создаем нового
            new_landlord = Landlords(
                user_id=create_landlord.user_id,
                company_name=create_landlord.company_name,
                phone=create_landlord.phone
            )
            self.session.add(new_landlord)
            await self.session.commit()
            await self.session.refresh(new_landlord)
            return new_landlord
        except Exception as e:
            await self.session.rollback()
            raise e  # Перекинем исключение дальше или обработаем его как нужно

