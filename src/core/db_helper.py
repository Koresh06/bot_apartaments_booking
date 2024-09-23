from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.engine import make_url
from src.core.config import DbConfig


class DatabaseHelper:
    def __init__(self, config: DbConfig):
        self.config = config
        self.engine = self.get_engine()
        self.sessionmaker = self.get_sessionmaker()

    def get_engine(self) -> AsyncEngine:
        return create_async_engine(url=make_url(self.config.url), echo=self.config.echo)

    def get_sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            autoflush=False
        )

    async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.sessionmaker() as session:
            yield session


db_helper = DatabaseHelper(DbConfig())