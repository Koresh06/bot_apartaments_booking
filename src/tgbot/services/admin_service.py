from src.core.repo.base import BaseRepo
from src.core.models import City, Users
from sqlalchemy import select, and_


class AdminBotRepo(BaseRepo):
    
    async def register_name_city(self, name: str) -> City:
        city = City(name=name)
        self.session.add(city)
        await self.session.commit()
        await self.session.refresh(city)
        return city
    

    async def check_is_admin(self, tg_id: int) -> bool:
        stmt = select(Users).where(Users.tg_id == tg_id)
        result = await self.session.scalar(stmt)
        return result
        