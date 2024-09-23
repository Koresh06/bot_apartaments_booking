from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from src.tgbot.services.users_bot_servise import BotUserRepo


@dataclass
class RequestsRepo:

    session: AsyncSession


    @property
    def users(self) -> BotUserRepo:
        
        return BotUserRepo(self.session)
    


