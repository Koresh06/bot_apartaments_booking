from datetime import date

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
