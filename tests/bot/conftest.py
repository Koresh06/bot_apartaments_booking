import pytest
import pytest_asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock

from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import Context
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State
from alembic.command import upgrade, downgrade
from alembic.config import Config as AlembicConfig
from src.core.config import load_config, Config
from src.tgbot.dialog import get_routers, get_all_dialogs
from src.tgbot.middlewares.db_session import DbSessionMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from aiogram_dialog.test_tools.memory_storage import JsonMemoryStorage
from aiogram_dialog.test_tools import BotClient, MockMessageManager

from .mocked_aiogram import MockedBot, MockedSession
from src.core.models.base import Base


# Фикстура для получения экземпляра фейкового бота
@pytest_asyncio.fixture(loop_scope="session", scope="session")
def bot() -> MockedBot:
    bot = MockedBot()
    bot.session = MockedSession()
    return bot


# Фикстура, которая получает объект настроек
@pytest_asyncio.fixture(loop_scope="session", scope="session")
def config() -> Config:
    return load_config(".env")


# Фикстура для получения асинхронного "движка" для работы с СУБД
@pytest_asyncio.fixture(loop_scope="session", scope="session")
def engine(config: Config):
    engine = create_async_engine(
    url=config.db.construct_sqlalchemy_url(is_test=True),
    echo=False,
    pool_pre_ping=True, 
    poolclass=NullPool
    )
    yield engine
    engine.sync_engine.dispose()


# Обновлённая фикстура для получения экземпляра диспетчера aiogram
# Здесь же надо ещё раз подключить все нужные мидлвари
@pytest_asyncio.fixture(loop_scope="session", scope="session")
def dp(engine) -> Dispatcher:
    usecase = Mock()
    user_getter = Mock(side_effect=["Username", ])
    dp = Dispatcher(
        usecase=usecase, 
        user_getter=user_getter,
        storage=JsonMemoryStorage(),
    )
    async_sessionmaker = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    dp.update.middleware(DbSessionMiddleware(sessionmaker=async_sessionmaker))
    dp.include_routers(*get_routers())
    dp.include_routers(*get_all_dialogs())
    return dp


# Фикстура, которая в каждом модуле применяет миграции
# А после завершения тестов в модуле откатывает базу к нулевому состоянию (без данных)
@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def create(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    yield engine

    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)


# Фикстура, которая передаёт в тест сессию из "движка"
@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def session(engine, create):
    async with AsyncSession(engine) as s:
        yield s


@pytest.fixture()
def mock_manager() -> DialogManager:
    manager = AsyncMock()
    context = Context(
        dialog_data={},
        start_data={},
        widget_data={},
        state=State(),
        _stack_id="_stack_id",
        _intent_id="_intent_id",
    )
    manager.current_context = Mock(side_effect=lambda: context)

    return manager


@pytest.fixture()
def message_manager() -> MockMessageManager:
    return MockMessageManager()