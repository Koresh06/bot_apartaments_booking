from typing import Optional
from pydantic import EmailStr
from sqlalchemy import select
from src.core.models import Users

from src.core.repo.base import BaseRepo
from src.apmin_panel.api.auth.security import verify_password, get_password_hash
from src.apmin_panel.api.auth.schemas import UserCreateInRegistration


class AuthApiRepo(BaseRepo):

    async def get_user_by_id(self, user_id: int):
        stmt = select(Users).where(Users.id == user_id)
        result = await self.session.scalar(stmt)
        
        return result


    async def create_admin(self, schema: UserCreateInRegistration):
        hash_password = get_password_hash(schema.password)
        stmt = select(Users).where(Users.id == schema.user_id)
        user: Users = await self.session.scalar(stmt)

        user.hashed_password = hash_password
        user.email = schema.email
        user.is_admin = True
        await self.session.commit()
        await self.session.refresh(user)
        return user


    async def authenticate(self, email: EmailStr, password: str) -> Optional[Users]:
        stmt = select(Users).where(Users.email == email)
        user: Users = await self.session.scalar(stmt)

        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    

    async def get_by_email(self, email: EmailStr):
        stmt = select(Users).where(Users.email == email)
        user: Users = await self.session.scalar(stmt)

        return user


    async def create_superuser(
            self, 
            email: EmailStr,
    ):
        stmt = select(Users).where(Users.email == email)
        user: Users = await self.session.scalar(stmt)

        if not user:
            return None
        
        user.is_superuser = True
        await self.session.commit()
        await self.session.refresh(user)
        return user

        
