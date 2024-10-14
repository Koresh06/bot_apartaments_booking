import asyncio
from typing import AsyncGenerator
import pytest
import pytest_asyncio

from asyncio import current_task

from httpx import ASGITransport, AsyncClient
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, async_scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool


from src.apmin_panel.api.auth_helpers import create_hashed_cookie
from src.tgbot.dialog import get_routers
from tests.mocked_aiogram import MockedBot, MockedSession

from src.core.db_helper import get_db
from src.core.config import Config, load_config
from src.core.models.base import Base
from src.run_fastapi import app
from src.core.config import config


engine = create_async_engine(
    url=config.db.construct_sqlalchemy_url(is_test=True),
    echo=False,
    pool_pre_ping=True, 
    poolclass=NullPool
)
async_session_maker = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False,)


async def ovverride_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_db] = ovverride_get_db


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client



@pytest_asyncio.fixture
async def authenticated_client(async_client: AsyncClient):
    # Устанавливаем валидный токен в куках
    valid_login = config.api.admin_login
    secret_key = config.api.secret_key
    token = create_hashed_cookie(valid_login, secret_key)  # Создаем хешированный токен
    async_client.cookies["admin_token"] = token  # Устанавливаем куки
    return async_client


@pytest.fixture(scope="session")
def dp() -> Dispatcher:
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_routers(*get_routers())
    return dispatcher


@pytest.fixture(scope="session")
def bot() -> MockedBot:
    bot = MockedBot()
    bot.session = MockedSession()
    return bot
