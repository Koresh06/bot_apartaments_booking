from typing import Optional

from sqlalchemy import select, Result
from src.core.models import Users, Landlords, ApartmentPhoto, Apartment

from src.core.repo.base import BaseRepo


class BotUserRepo(BaseRepo):

    async def add_user(
        self,
        tg_id: int,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
    ):
        stmt = select(Users).where(Users.tg_id == tg_id)
        result: Result = await self.session.scalar(stmt)

        if result:
            return
        stmt = Users(
            tg_id=tg_id,
            username=username,
            full_name=full_name,
        )
        self.session.add(stmt)
        await self.session.commit()
        await self.session.refresh(stmt)
        return False


    async def add_handler(
            self, 
            tg_id: int,
            company_name: str,
            phone: str,
    ):
        stmt = select(Users).where(Users.tg_id == tg_id)
        result: Users = await self.session.scalar(stmt)
        landlord = Landlords(
            user_id=result.id,
            company_name=company_name,
            phone=phone,
        )

        self.session.add(landlord)    
        await self.session.commit()
        await self.session.refresh(landlord)

