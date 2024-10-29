from datetime import date
from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.orm import selectinload
from src.core.models import Landlords, Users, Apartment, Booking, City

from src.core.repo.base import BaseRepo
from .schemas import CreateLandlordSchema


class LandlordApiRepo(BaseRepo):

    async def get_paginated_landlords(self, page: int, size: int):
        offset = (page - 1) * size
        stmt = (
            select(Landlords)
            .options(selectinload(Landlords.user_rel))
            .order_by(Landlords.id.desc()) 
            .offset(offset)
            .limit(size)
        )

        result = await self.session.execute(stmt)
        landlords = result.scalars().all()

        return landlords if landlords else []


    async def count_all_landlords(self):
        query = select(func.count(Landlords.id))
        result = await self.session.execute(query)
        total = result.scalar()
    
        return total if total else 0
    

    async def get_statistics_by_landlord_id(
    self,
    landlord_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
        stmt = select(Landlords).join(Users).options(selectinload(Landlords.user_rel)).where(Landlords.id == landlord_id)
        result = await self.session.execute(stmt)
        landlord = result.scalar()

        if not landlord:
            return "Арендодатель не найден"

        # Получаем апартаменты арендодателя
        stmt_apartments = select(Apartment).where(Apartment.landlord_id == landlord_id)
        result_apartments = await self.session.execute(stmt_apartments)
        apartments = result_apartments.scalars().all()

        total_apartments = len(apartments) if apartments else "Нет данных"

        # Получаем завершенные бронирования
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

        # Инициализация переменной для общего дохода
        total_income = 0

        # Создаем словарь для быстрого поиска квартир по их ID
        apartment_dict = {apt.id: apt for apt in apartments}

        # Проходим по завершенным бронированиям
        for booking in completed_bookings:
            # Получаем соответствующую квартиру из словаря
            apartment = apartment_dict.get(booking.apartment_id)

            if apartment:  # Проверяем, была ли найдена квартира
                # Вычисляем количество дней, за которые была забронирована квартира
                days_booked = (booking.end_date - booking.start_date).days
                # Увеличиваем общий доход
                total_income += apartment.price_per_day * days_booked

        # Если доход не был увеличен, устанавливаем значение "Нет данных"
        total_income = total_income if total_income > 0 else "Нет данных"

        return {
            "landlord": landlord,
            "apartments": apartments,
            "total_apartments": total_apartments,
            "total_completed_bookings": total_completed_bookings,
            "total_pending_bookings": total_pending_bookings,
            "total_income": total_income,
        }
    

    async def get_paginated_completed_bookings_by_landlord_id(self, landlord_id: int, page: int, size: int):
        offset = (page - 1) * size
        landlord = await self.session.scalar(select(Landlords).where(Landlords.id == landlord_id))

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
            .where(Booking.is_completed == True, Apartment.landlord_id == landlord.id)
            .order_by(Booking.id.desc())
            .offset(offset)
            .limit(size)
        )
        result = await self.session.execute(stmt)
        bookings_with_details = result.all()

        return bookings_with_details
    

    async def count_all_completed_bookings_by_landlord_id(self, landlord_id: int):
        landlord = await self.session.scalar(select(Landlords).where(Landlords.id == landlord_id))
        query = (
            select(func.count(Booking.id))
            .where(Booking.is_completed == True, Booking.user_id == landlord.user_id)
        )
        result = await self.session.execute(query)
        total = result.scalar()

        return total


    async def get_paginated_pending_bookings_by_landlord_id(self, landlord_id: int, page: int, size: int):
        offset = (page - 1) * size
        landlord = await self.session.scalar(select(Landlords).where(Landlords.id == landlord_id))

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
            .join(Landlords, Apartment.landlord_id == Landlords.id)
            .where(and_(Booking.is_completed == False, Apartment.landlord_id == landlord.id))
            .order_by(Booking.id.desc())
            .offset(offset)
            .limit(size)
        )
        result = await self.session.execute(stmt)
        bookings_with_details = result.all()

        return bookings_with_details
    

    async def count_all_pending_bookings_by_landlord_id(self, landlord_id: int):
        landlord = await self.session.scalar(select(Landlords).where(Landlords.id == landlord_id))
        query = (
            select(func.count(Booking.id))
            .where(Booking.is_completed == False, Booking.user_id == landlord.user_id)
        )
        result = await self.session.execute(query)
        total = result.scalar()

        return total


    async def get_paginated_total_income_bookings_by_landlord_id(self, landlord_id: int, page: int, size: int):
        offset = (page - 1) * size
        landlord = await self.session.scalar(select(Landlords).where(Landlords.id == landlord_id))

        stmt = (
            select(
                Booking,
                Users.username,
                Apartment.street,
                Apartment.house_number,
                Apartment.apartment_number,
                City.name.label('city_name'),
                Apartment.price_per_day,
            )
            .join(Users, Booking.user_id == Users.id) 
            .join(Apartment, Booking.apartment_id == Apartment.id) 
            .join(City, Apartment.city_id == City.id) 
            .join(Landlords, Apartment.landlord_id == Landlords.id) 
            .where(Booking.is_completed == True, Apartment.landlord_id == landlord.id)
            .order_by(Booking.id.desc())
            .offset(offset)
            .limit(size)
        )

        
        result = await self.session.execute(stmt)
        bookings_with_details = result.all()  

        bookings_with_income = []

        for booking, username, street, house_number, apartment_number, city_name, price_per_day in bookings_with_details:
     
            days_booked = (booking.end_date - booking.start_date).days

            booking_income = price_per_day * days_booked

            bookings_with_income.append({
                'booking': booking,
                'username': username,
                'street': street,
                'house_number': house_number,
                'apartment_number': apartment_number,
                'city_name': city_name,
                'income': booking_income, 
                'created_at': booking.create_at 
            })

        return bookings_with_income
    

    async def count_all_total_income_bookings_by_landlord_id(self, landlord_id: int):
        landlord = await self.session.scalar(select(Landlords).where(Landlords.id == landlord_id))
        query = (
            select(func.count(Booking.id))
            .where(Booking.is_completed == True, Booking.user_id == landlord.user_id)
        )
        result = await self.session.execute(query)
        total = result.scalar()

        return total
    

    async def get_users_not_landlord(self):
        stmt = (
            select(Users)
            .outerjoin(Landlords, Users.id == Landlords.user_id) 
            .filter(Landlords.user_id.is_(None))  
        )

        result = await self.session.execute(stmt)
        users_not_landlords = result.scalars().all()  

        return users_not_landlords
    

    async def create_landlord(self, create_landlord: CreateLandlordSchema):
        existing_landlord = await self.session.execute(
            select(Landlords).filter(Landlords.user_id == create_landlord.user_id)
        )
        if existing_landlord.scalars().first() is not None:
            raise ValueError(f"Арендодатель с user_id {create_landlord.user_id} уже существует.")
        new_landlord = Landlords(
            user_id=create_landlord.user_id,
            company_name=create_landlord.company_name,
            phone=create_landlord.phone
        )
        self.session.add(new_landlord)
        await self.session.commit()
        await self.session.refresh(new_landlord)
        return new_landlord


    async def click_contact_landlord(self, tg_id: int):
        stmt = (
            select(Landlords)
            .join(Users, Landlords.user_id == Users.id)
            .where(Users.tg_id == tg_id)
        )
        result = await self.session.execute(stmt)
        landlord = result.scalars().first()

        if not landlord:
            return False
        
        landlord.count_clicks_phone += 1
        await self.session.commit()
        await self.session.refresh(landlord)

        return landlord