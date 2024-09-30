from typing import Any, Callable

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.repo.requests import RequestsRepo
from src.tgbot.dialog.bg_manager_factory import MyBgManagerFactory


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession], bg_manager: MyBgManagerFactory, bot: Bot) -> None:
        super().__init__()
        self.sessionmaker = sessionmaker
        self.bg_manager = bg_manager
        self.bot = bot

    async def __call__(self, handler: Callable, event: TelegramObject, data: dict) -> Any:
        async with self.sessionmaker() as session:
            repo = RequestsRepo(session)
            data["repo"] = repo
            data["session"] = session
            data["bg_manager"] = self.bg_manager
            data["bot"] = self.bot
            result = await handler(event, data)
        return result
