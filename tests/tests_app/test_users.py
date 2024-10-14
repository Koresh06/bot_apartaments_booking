from datetime import datetime
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.apmin_panel.api.services.users_api_service import UsersApiRepo
from src.core.models import Users
from ..conftest import async_session_maker


async def test_not_authenticated_client(async_client: AsyncClient, prepare_database):
    response = await async_client.get("/users/get-users/")
    assert response.status_code == 302
    assert response.headers["Location"] == "/auth/login"


async def test_get_users(authenticated_client: AsyncClient, prepare_database): 
    async with async_session_maker() as session:
        user1 = Users(
            id=1,
            tg_id=123456789,
            chat_id=987654321,
            username="user1",
            full_name="User One",
            is_admin=False,
            is_banned=False,
            create_at=datetime(2024, 1, 1, 12, 0),
            update_at=datetime(2024, 1, 1, 12, 0),
        )
        session.add(user1)
        user2 = Users(
            id=2,
            tg_id=223456789,
            chat_id=887654321,
            username="user2",
            full_name="User Two",
            is_admin=False,
            is_banned=False,
            create_at=datetime(2024, 1, 2, 12, 0),
            update_at=datetime(2024, 1, 2, 12, 0),
        )

        session.add(user2)
        await session.commit()

        stmt = select(Users)
        result: Users = await session.execute(stmt)
        users = result.scalars().all()
        assert len(users) == 2
        assert users[0] == user1
        assert users[1] == user2

        response = await authenticated_client.get("/users/get-users/")
        assert response.status_code == 200


async def test_get_user_detail(authenticated_client: AsyncClient, prepare_database): 
    user_id = 1
    response = await authenticated_client.get(f"/users/get-user-detail/{user_id}",)

    assert response.status_code == 200

    async with async_session_maker() as session:
        user_from_db = await UsersApiRepo(session).get_user_by_id(user_id)

    assert user_from_db.id == user_id 
    assert user_from_db.username == "user1"


async def test_banned_user(authenticated_client: AsyncClient, prepare_database): 
    user_id = 1
    response = await authenticated_client.post(f"/users/{user_id}/banned",)

    assert response.status_code == 200

    async with async_session_maker() as session:
        user_from_db = await UsersApiRepo(session).get_user_by_id(user_id)

    assert user_from_db.id == user_id 
    assert user_from_db.is_banned == True


async def test_unbanned_user(authenticated_client: AsyncClient, prepare_database):
    user_id = 1
    response = await authenticated_client.post(f"/users/{user_id}/unbanned",)

    assert response.status_code == 200

    async with async_session_maker() as session:
        user_from_db = await UsersApiRepo(session).get_user_by_id(user_id)

    assert user_from_db.id == user_id 
    assert user_from_db.is_banned == False




