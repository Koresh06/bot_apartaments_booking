from datetime import date, datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.core.models import Landlords, Users, Apartment, Booking

from src.core.repo.base import BaseRepo


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
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
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

        # Подсчитываем общее количество апартаментов
        total_apartments = len(apartments) if apartments else "Нет данных"

        # Подсчитываем общее количество завершенных бронирований
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
        total_completed_bookings = len(completed_bookings) if completed_bookings else "Нет данных"

        # Подсчитываем количество бронирований в работе
        stmt_pending_bookings = select(Booking).where(
            Booking.apartment_id.in_([apartment.id for apartment in apartments]),
            Booking.is_confirmed == True,
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
        total_pending_bookings = len(pending_bookings) if pending_bookings else "Нет данных"

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
            "total_pending_bookings": total_pending_bookings,
            "total_income": total_income,
        }

