from typing import Optional

from sqlalchemy import select, Result
from src.core.models import Users, Landlords

from src.core.repo.base import BaseRepo


class BotUserRepo(BaseRepo):

    async def check_new_user(self, tg_id: int):
        stmt = select(Users).where(Users.tg_id == tg_id)
        result: Result = await self.session.scalar(stmt)

        if result:
            return True
        return False
    
    
    async def check_landlord(self, tg_id: int):
        stmt = select(Landlords).where(Landlords.user_id == tg_id)
        result: Result = await self.session.scalar(stmt)

        if result:
            return True
        return False