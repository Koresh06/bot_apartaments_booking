

from src.core.repo.base import BaseRepo
from src.core.models import City


class AdminRepo(BaseRepo):
    
    async def register_name_city(self, name: str) -> City:
        city = City(name=name)
        self.session.add(city)
        await self.session.commit()
        await self.session.refresh(city)
        return city