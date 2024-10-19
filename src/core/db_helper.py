from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.config import config


# class DatabaseHelper:
#     def __init__(self, config: DbConfig, is_test: bool = False):
#         self.config = config
#         self.is_test = is_test  # Флаг для выбора тестовой базы
#         self.engine = self.create_engine(config, echo=False)
#         self.sessionmaker = self.create_session_pool(self.engine)


#     def create_engine(self, db: DbConfig, echo=False) -> AsyncEngine:
#         return create_async_engine(
#             db.construct_sqlalchemy_url(is_test=self.is_test),
#             query_cache_size=1200,
#             pool_size=20,
#             max_overflow=200,
#             future=True,
#             echo=echo
#         )
    


#     def create_session_pool(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
#         return async_sessionmaker(
#             bind=engine,
#             expire_on_commit=False
#         )


#     async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
#         async with self.sessionmaker() as session:
#             yield session


# db_helper = DatabaseHelper(config=config.db)

engine = create_async_engine(
    url=config.db.construct_sqlalchemy_url(),
    query_cache_size=1200,
    pool_size=20,
    max_overflow=200,
    future=True,
    echo=False,
)


async_session_maker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            # Обработка исключения (если нужно, например, логирование)
            print(f"Ошибка при работе с сессией: {e}")
            raise  # Перебрасываем исключение, чтобы FastAPI мог его обработать
        finally:
            await session.close()  # Закрываем сессию в любом случае