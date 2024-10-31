from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from src.core.models import Apartment

from src.core.models import Landlords
from src.core.repo.base import BaseRepo


class ApartmentApiRepo(BaseRepo):
    

    async def get_paginated_apartments(self, page: int, size: int):
        offset = (page - 1) * size
        query = (
            select(Apartment)
            .options(
                selectinload(Apartment.city_rel),
                selectinload(Apartment.landlord_rel)
            )
            .order_by(Apartment.id.desc())  
            .offset(offset)
            .limit(size)
        )
        result = await self.session.execute(query)
        apartments = result.scalars().all() 

        return apartments
    

    async def count_all_apartments(self):
        query = select(func.count(Apartment.id))
        result = await self.session.execute(query)
        total = result.scalar()

        return total
    

    async def get_apartment_by_landlord(self, landlord_id: int):
        query = (
            select(Apartment)
            .options(
                selectinload(Apartment.city_rel),
                selectinload(Apartment.landlord_rel)
            )
            .where(Apartment.landlord_id == landlord_id)
        )
        result = await self.session.execute(query)
        apartments = result.scalars().all() 

        return apartments
    

    async def get_landlord_by_id(self, landlord_id: int):
        query = select(Landlords).where(Landlords.id == landlord_id)
        result = await self.session.execute(query)
        landlord = result.scalar()

        return landlord