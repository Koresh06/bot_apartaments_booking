from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from src.tgbot.services.users_bot_service import BotUserRepo
from src.tgbot.services.apartments_bot_service import BotApartmentRepo


@dataclass
class RequestsRepo:

    session: AsyncSession


    @property
    def bot_users(self) -> BotUserRepo:
        
        return BotUserRepo(self.session)
    

    @property
    def bot_apartments(self) -> BotApartmentRepo:
        
        return BotApartmentRepo(self.session)
    


