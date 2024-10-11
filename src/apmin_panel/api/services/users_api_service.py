from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.core.models import Landlords, Users

from src.core.repo.base import BaseRepo

class UsersApiRepo(BaseRepo):

    async def get_all_users(self):
        query = (
            select(Users)
            .options(selectinload(Users.landlord_rel)) 
            .order_by(Users.id.desc())
        )
        result = await self.session.execute(query)
        users = result.scalars().all()

        return users


    async def get_user_by_id(self, user_id: int):
        query = (
            select(Users)
            .options(selectinload(Users.landlord_rel).selectinload(Landlords.apartment_rel)) 
            .where(Users.id == user_id)
        )
        result = await self.session.execute(query)
        user = result.scalar()

        return user


    async def banned_user_by_id(self, user_id: int):
        query = (
            select(Users)
            .where(Users.id == user_id)
        )
        result = await self.session.execute(query)
        user = result.scalar()

        user.is_banned = True
        await self.session.commit()
        await self.session.refresh(user)
        return user
    

    async def unbanned_user_by_id(self, user_id: int):
        query = (
            select(Users)
            .where(Users.id == user_id)
        )
        result = await self.session.execute(query)
        user = result.scalar()

        user.is_banned = False
        await self.session.commit()
        await self.session.refresh(user)
        return user