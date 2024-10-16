from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from src.apmin_panel.api.auth.schemas import UserCreateInRegistration
from src.core.models import Landlords, Users

from src.core.repo.base import BaseRepo

class UsersApiRepo(BaseRepo):

    async def get_paginated_users(self, page: int, size: int):
        offset = (page - 1) * size
        query = (
            select(Users)
            .options(selectinload(Users.landlord_rel))
            .order_by(Users.id.desc())
            .offset(offset)
            .limit(size)
        )
        result = await self.session.execute(query)
        users = result.scalars().all()

        return users

    async def count_all_users(self):
        query = select(func.count(Users.id))
        result = await self.session.execute(query)
        total = result.scalar()

        return total


    async def get_user_by_id(self, user_id: int):
        query = (
            select(Users)
            .options(selectinload(Users.landlord_rel).selectinload(Landlords.apartment_rel)) 
            .where(Users.id == user_id)
        )
        result = await self.session.execute(query)
        user = result.scalar()

        return user
    
    async def get_users_not_admin(self):
        stmt = (
            select(Users)
            .filter(Users.is_admin == False or Users.is_superuser == False)
            .order_by(Users.id.desc())
        )

        result = await self.session.execute(stmt)
        users = result.scalars().all()

        return users
    
    # async def create_admin(self, schema: UserCreateInRegistration):
    #     existing_admin = await self.session.scalar(
    #         select(Users).filter(Users.id == user_id)
    #     )
    #     if existing_admin.is_admin:
    #         raise ValueError(f"Админ с user_id {user_id} уже существует.")
        
    #     existing_admin.is_admin = True
    #     await self.session.commit()
    #     await self.session.refresh(existing_admin)
    #     return existing_admin
        
        



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