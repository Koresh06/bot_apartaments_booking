from typing import Awaitable, Callable, Any, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.models.users import Users

from ..services.users_bot_service import BotUserRepo


class BanCheckMiddleware(BaseMiddleware):
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        super().__init__()
        self.sessionmaker = sessionmaker

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        session: AsyncSession = data.get("session")  # Получаем сессию из data

        tg_id = event.from_user.id
            
        repo = BotUserRepo(session)  # Используем сессию для создания репозитория
        user: Users = await repo.check_user_ban_status(
            tg_id=tg_id,
            chat_id=event.chat.id,
            username=event.from_user.username,
            first_name=event.from_user.first_name,
            last_name=event.from_user.last_name,
            full_name=event.from_user.full_name,
        )

        if user.is_banned:
            reply_text = "Вы заблокированы и не можете использовать бота."
            if isinstance(event, Message):
                await event.answer(reply_text)
            return  # Не продолжать обработку

        # Передаем управление следующему обработчику
        return await handler(event, data)
    
