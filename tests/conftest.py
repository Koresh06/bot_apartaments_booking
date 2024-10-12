import pytest

from httpx import ASGITransport, AsyncClient
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.apmin_panel.api.auth_helpers import create_hashed_cookie
from src.tgbot.dialog import get_routers
from tests.mocked_aiogram import MockedBot, MockedSession

from src.core.db_helper import DatabaseHelper
from src.core.config import Config, load_config
from src.core.models.base import Base
from src.run_fastapi import app


@pytest.fixture(scope="session")
def test_config() -> Config:
    """
    Фикстура для подгрузки конфигурации для тестовой среды.
    """
    return load_config(path=".env")


@pytest.fixture(scope="session", autouse=True)
async def setup_test_database(test_config: Config):
    """
    Настройка тестовой базы данных, создание таблиц до тестов и их удаление после тестов.
    """
    test_db_helper = DatabaseHelper(config=test_config.db, is_test=True)

    async with test_db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield test_db_helper

    async with test_db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def overrides_get_async_session(setup_test_database: DatabaseHelper):
    async def _get_test_db():
        async with setup_test_database.sessionmaker() as session:
            yield session

    app.dependency_overrides[setup_test_database.get_db] = _get_test_db

    yield _get_test_db


@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client



@pytest.fixture
async def authenticated_client(async_client: AsyncClient):
    # Устанавливаем валидный токен в куках
    valid_login = "admin_login"  # Замените на актуальное значение
    secret_key = "your_secret_key"  # Замените на актуальное значение
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
