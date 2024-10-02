from typing import Any, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.repo.requests import RequestsRepo


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        super().__init__()
        self.sessionmaker = sessionmaker
        

    async def __call__(self, handler: Callable, event: TelegramObject, data: dict) -> Any:
        async with self.sessionmaker() as session:
            repo = RequestsRepo(session)
            data["repo"] = repo
            data["session"] = session
            result = await handler(event, data)
        return result
