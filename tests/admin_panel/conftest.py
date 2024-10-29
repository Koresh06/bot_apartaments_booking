from typing import AsyncGenerator
import pytest
import pytest_asyncio

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from src.core.db_helper import get_db
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
    
    return async_client


